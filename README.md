# AI Code Review Assistant

README prose word count: approximately 330 words (excluding headings, code commands and file names).

## Project status

This is a student web prototype for exploring how feedback can support users when evaluating AI-generated Python code. The prototype implements code input, syntax parsing, simple static checks, explanatory feedback, illustrative check scenarios, and Accept / Reject / Edit decisions. Decision history is saved in the user's browser using local storage.

**Important limitation:** The project does not connect to a real AI model, does not execute submitted code, and does not run unit tests. The feedback is produced by transparent Python syntax and pattern-based rules. The name “test feedback” refers to illustrative static checks, not actual test execution. The simple name checker is incomplete and may produce false positives or miss problems. This is not a production code-security or correctness tool.

## Technology stack

- Python 3.10 or later and Flask: web server and analysis endpoint.
- Python `ast`: parse code and inspect syntax and selected code patterns without executing it.
- HTML and CSS: user interface.
- JavaScript: API requests, rendering feedback, and recording decisions in browser local storage.
- `unittest`: basic checks for the analysis function.

## Run locally

1. Open a terminal in this project folder.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it in Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Start the app: `python app.py`
6. Open `http://127.0.0.1:5000` in a browser.

To run the analysis tests, use `python -m unittest discover -s tests`.

## Main interactions

1. Paste a Python code suggestion and select **Analyse code**.
2. Review the explanation, static check scenarios, and potential issues.
3. Select **Accept**, **Reject**, or **Edit**. The decision, time, short code preview and analysis summary appear in Decision history.
4. Decision history remains in the same browser on that device. **Clear history** removes the locally stored records.

## Development record

- Initial version: Flask page with a code editor, basic syntax parsing and feedback panel.
- Iteration 2: added compile-time checking, a more explicit possible-undefined-name warning, pattern-based edge-case feedback, and structured illustrative check scenarios.
- Iteration 2: implemented decision recording and a visible history list using browser local storage. Added a clear-history action.
- Verification: run the included `unittest` suite and manually check syntax-error, undefined-name, valid-function, and decision-history scenarios before submission.

## AI assistance

AI assistance was used to help plan the prototype, draft and revise code, and prepare documentation. The developer should inspect the implementation, run the application and tests, verify the interface in a browser, and make sure the final report accurately describes the implemented and simulated features. Record any additional tools and manual changes actually used before submission.

## Additional files

- `templates/`: HTML page.
- `static/`: CSS and JavaScript.
- `tests/`: automated analysis checks.
- `screenshots/`: screenshots captured by the developer for the report.
- `diagrams/`: system diagram and design materials.
