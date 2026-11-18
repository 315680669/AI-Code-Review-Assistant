import unittest
from app import analyse_code


class AnalysisTests(unittest.TestCase):
    def test_detects_syntax_error(self):
        result = analyse_code("def broken(:\n    return 1")
        self.assertEqual(result["test_status"], "Not run")
        self.assertEqual(result["issues"][0]["title"], "Syntax error")

    def test_detects_obvious_undefined_name(self):
        result = analyse_code("def calculate_average(numbers):\n    return total / len(numbers)")
        titles = [issue["title"] for issue in result["issues"]]
        self.assertIn("Possible undefined name", titles)
        self.assertIn("total", result["issues"][0]["detail"])

    def test_simple_valid_function_has_no_obvious_issue(self):
        code = ("def calculate_average(numbers):\n"
                "    if not numbers:\n"
                "        return 0\n"
                "    return sum(numbers) / len(numbers)")
        result = analyse_code(code)
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["checks"])

    def test_empty_input(self):
        result = analyse_code("   ")
        self.assertEqual(result["test_status"], "Not run")
        self.assertEqual(result["issues"][0]["title"], "Empty input")


if __name__ == "__main__":
    unittest.main()
