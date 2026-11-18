```markdown
# Storyboards for AI Code Review Assistant

## Storyboard 1: User Discovers an Error in AI-Generated Code (Case 1)

### Frame 1 — Code Input
* **User Action:** The user receives a Python snippet from an AI coding assistant and pastes it directly into the CodeReview web application's input box.
* **Code Example:**
  ```python
  def calculate_average(numbers):
      return total / len(numbers)

```

* **System State:** The application is ready to accept and parse the submitted text.

### Frame 2 — Analyse Code

* **User Action:** The user clicks the **Analyse code** button.
* **System Response:** The Flask backend performs static AST inspection and checks variable usage. It detects that the variable `total` is used in the expression without being defined anywhere in the function scope.

### Frame 3 — Review Feedback

* **System Response:** The system displays a warning message reading **"Possible undefined name"**, accompanied by an explanation that `total` is used before assignment.
* **User Experience:** The user reviews the feedback, realizes the AI-generated code contains a critical bug, and decides not to trust it blindly.

### Frame 4 — Reject

* **User Action:** The user clicks the **Reject** button.
* **System Response:** The application records the decision, updates the local storage, and logs the action in the **Decision history** section.

---

* **HCI Principles Demonstrated:**
* **Visibility of System Status:** The system clearly highlights and flags the detected error.
* **Feedback:** Explains why the code requires attention rather than just giving a binary pass/fail.
* **User Control:** The user retains full autonomy over whether to accept or reject the AI's output.



---

## Storyboard 2: User Reviews and Accepts a Reliable Code Snippet (Case 2)

### Frame 1 — Code Input

* **User Action:** The user inputs a robust Python function designed to calculate an average, complete with a safeguard check for empty lists.
* **Code Example:**
```python
def calculate_average(numbers):
    if not numbers:
        return 0.0
    total = sum(numbers)
    return total / len(numbers)

```



### Frame 2 — Analyse Code

* **User Action:** The user clicks **Analyse code**.
* **System Response:** The application scans the rules and executes static analysis checks.

### Frame 3 — Review Feedback

* **System Response:** The system displays **"No obvious issue detected"**, while gently reminding the user that this does not guarantee absolute correctness and manual review is still recommended.

### Frame 4 — Accept

* **User Action:** After reading the feedback, the user clicks **Accept**.
* **System Response:** The application saves the decision and logs it into the **Decision history**.

---

* **HCI Principles Demonstrated:**
* **Visibility of System Status:** Clearly exhibits the current code inspection status.
* **Feedback:** Not only displays inspection results but also highlights the limitations of automated checks.
* **Informed Decision-making:** Empowers users to make decisions based on constructive feedback rather than blindly trusting AI-generated code.



---

## Storyboard 3: User Identifies a Potential Boundary Issue and Chooses to Edit (Case 3)

### Frame 1 — Code Input

* **User Action:** The user inputs an average calculation function that omits checks for empty lists.
* **Code Example:**
```python
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

```



### Frame 2 — Potential Issue

* **System Response:** The system detects a potential boundary risk where an empty list could trigger a `ZeroDivisionError`, prompting the user to check this edge case.

### Frame 3 — Edit

* **User Action:** Deciding not to blindly accept or reject, the user clicks **Edit** and manually updates the code to include an empty list guard condition (`if not numbers: return 0.0`).

### Frame 4 — Re-analyse

* **User Action:** The user re-submits the modified code for analysis.
* **System Response:** The system finds no obvious issues and logs the user's **Edit** action into the history.

---

* **HCI Principles Demonstrated:**
* **Error Prevention:** Proactively warns about potential edge cases to help users avoid runtime bugs.
* **User Control and Freedom:** Allows users to modify code directly instead of being restricted to binary accept/reject choices.
* **Feedback:** Enables a continuous feedback loop where users can re-analyze after making modifications.



```

```