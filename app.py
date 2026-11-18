from flask import Flask, render_template, request, jsonify
import ast
import builtins

app = Flask(__name__)


class NameUsageVisitor(ast.NodeVisitor):
    """Collect names loaded and bound in a deliberately lightweight way.

    This is a teaching prototype, not a replacement for a Python linter.
    Function-local scopes are handled approximately; class/comprehension and
    closure semantics are intentionally outside this prototype's scope.
    """
    def __init__(self):
        self.loaded = []
        self.bound = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.loaded.append((node.id, node.lineno))
        elif isinstance(node.ctx, (ast.Store, ast.Param)):
            self.bound.add(node.id)

    def visit_FunctionDef(self, node):
        self.bound.add(node.name)
        # Do not descend into the function body here: its local names belong
        # to a separate scope. Defaults and decorators execute in outer scope.
        for item in node.decorator_list + node.args.defaults + [d for d in node.args.kw_defaults if d]:
            self.visit(item)
        for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
            pass

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.bound.add(node.name)
        for item in node.decorator_list + node.bases + node.keywords:
            self.visit(item)


def _function_parameters(function_node):
    args = function_node.args
    all_args = args.posonlyargs + args.args + args.kwonlyargs
    if args.vararg:
        all_args.append(args.vararg)
    if args.kwarg:
        all_args.append(args.kwarg)
    return {arg.arg for arg in all_args}


def _static_test_feedback(tree, issues):
    """Return illustrative checks; submitted code is never executed."""
    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    function_names = [fn.name for fn in functions]
    checks = []

    if any(i["title"] in {"Syntax error", "Compile-time error", "Possible undefined name"} for i in issues):
        checks.append({
            "name": "Basic code validity",
            "input": "Parse and inspect the submitted snippet",
            "expected": "No syntax or obvious name-resolution problems",
            "result": "Concern found",
            "detail": "The static checks found an issue that should be reviewed before the code is trusted."
        })
    else:
        checks.append({
            "name": "Basic code validity",
            "input": "Parse and inspect the submitted snippet",
            "expected": "Valid Python syntax and no obvious undefined names",
            "result": "No issue detected",
            "detail": "This is a static inspection result, not proof that the program runs correctly."
        })

    if function_names:
        for fn in functions[:3]:
            checks.append({
                "name": f"Function review: {fn.name}()",
                "input": "Inspect function definition and return paths",
                "expected": "Function should handle its intended inputs",
                "result": "Manual review needed",
                "detail": "The prototype does not execute the function or know its full specification. Check normal and edge-case inputs."
            })
    else:
        checks.append({
            "name": "Function behaviour",
            "input": "No function definition detected",
            "expected": "A clearly defined callable operation, if one is required",
            "result": "Not applicable",
            "detail": "No function was found, so function-level examples cannot be assessed."
        })

    source = ast.unparse(tree) if hasattr(ast, "unparse") else ""
    if "len(" in source and "/" in source and not any(word in source for word in ("if not", "if len", "== 0")):
        checks.append({
            "name": "Possible empty-input edge case",
            "input": "An empty collection, e.g. []",
            "expected": "A clear result or handled error",
            "result": "Review required",
            "detail": "The code appears to divide by a collection length. Consider what happens when that collection is empty. This is a pattern-based warning."
        })

    return checks


def analyse_code(code: str) -> dict:
    """Rule-based static review for the student prototype; never executes code."""
    if not code.strip():
        return {
            "status": "No code provided",
            "issues": [{"severity": "warning", "title": "Empty input", "detail": "Enter a Python code snippet before starting the analysis."}],
            "test_status": "Not run",
            "explanation": "There is no code to explain yet.",
            "summary": "Please enter some code.",
            "checks": []
        }

    issues = []
    try:
        tree = ast.parse(code)
        # compile() checks additional compile-time restrictions but does not run code.
        compile(tree, "<submitted-snippet>", "exec")
    except SyntaxError as exc:
        issues.append({"severity": "error", "title": "Syntax error", "detail": f"{exc.msg} (line {exc.lineno})"})
        return {
            "status": "Issues detected", "issues": issues, "test_status": "Not run",
            "explanation": "The code could not be parsed because it contains a Python syntax error.",
            "summary": "The code has a syntax error. Correct it before reviewing behaviour.",
            "checks": [{"name": "Syntax inspection", "input": "Parse submitted Python", "expected": "Valid Python syntax", "result": "Failed", "detail": f"Parser reported: {exc.msg} on line {exc.lineno}."}]
        }
    except (ValueError, TypeError) as exc:
        issues.append({"severity": "error", "title": "Compile-time error", "detail": str(exc)})

    # Top-level name checks are intentionally conservative and do not claim
    # complete scope analysis. Collect names in the module and function bodies.
    module_visitor = NameUsageVisitor()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            module_visitor.visit(node)
        elif isinstance(node, ast.ClassDef):
            module_visitor.visit(node)
        else:
            module_visitor.visit(node)

    bound_names = set(module_visitor.bound)
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        bound_names.update(_function_parameters(fn))
        # Include names used inside functions and their simple local bindings.
        for child in ast.walk(fn):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                module_visitor.loaded.append((child.id, child.lineno))
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                bound_names.add(child.id)
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                for alias in child.names:
                    bound_names.add(alias.asname or alias.name.split('.')[0])

    builtin_names = set(dir(builtins))
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                imported_names.add(alias.asname or alias.name.split('.')[0])

    # Only flag names whose use cannot be matched to any simple binding.
    # This may miss scope errors; that limitation is disclosed in the UI.
    for name, line in sorted(set(module_visitor.loaded), key=lambda item: (item[1], item[0])):
        if name not in bound_names and name not in builtin_names and name not in imported_names and name not in {"self", "cls"}:
            issues.append({"severity": "error", "title": "Possible undefined name", "detail": f"'{name}' is used but no matching definition was found in this snippet (line {line})."})

    source = code.lower()
    if "eval(" in source or "exec(" in source:
        issues.append({"severity": "warning", "title": "Dynamic code execution", "detail": "The snippet contains eval() or exec(). Review the source and input carefully because dynamic execution can be unsafe."})

    if any(isinstance(n, ast.FunctionDef) and not n.body for n in ast.walk(tree)):
        issues.append({"severity": "warning", "title": "Empty function", "detail": "A function has no body. Add an implementation or an explicit pass statement."})

    functions = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if functions:
        explanation = "The snippet defines " + ", ".join(functions) + ". The prototype checks syntax, simple name usage and selected code patterns. It does not fully understand the program's intended behaviour."
    else:
        explanation = "The snippet has valid Python syntax. The prototype checks simple name usage and selected code patterns, but it does not fully understand the program's intended behaviour."

    checks = _static_test_feedback(tree, issues)
    if issues:
        status = "Issues detected"
        test_status = "Review required"
        summary = "The static review found potential problems. Review each finding; no code was executed."
    else:
        status = "No issues detected by current checks"
        test_status = "No obvious issue detected"
        summary = "The current checks did not find an obvious problem. This is not a real test pass and does not guarantee correctness."

    return {"status": status, "issues": issues, "test_status": test_status,
            "explanation": explanation, "summary": summary, "checks": checks}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyse", methods=["POST"])
def analyse():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not isinstance(code, str):
        return jsonify({"error": "Code must be submitted as text."}), 400
    return jsonify(analyse_code(code))


if __name__ == "__main__":
    app.run(debug=True)
