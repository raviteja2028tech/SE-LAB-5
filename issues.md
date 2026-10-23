# Lab 5: Static Code Analysis — Issues Report

**Target File:** `energy_system.py`  
**Analyzers Used:** Bandit v1.9.4, Flake8 v7.4.1, Pylint v4.1.3  
**Final Pylint Score:** **10.00 / 10** (Improved from initial **6.14 / 10**)

---

## 1. Summary of Identified Issues

The static analysis scan and manual inspection identified security vulnerabilities, code style violations, anti-patterns, and semantic logic bugs. Below is the structured issue tracking table ordered with high and medium severity issues first.

| Issue | Type | Line(s) | Description | Fix Approach |
|:------|:-----|:--------|:------------|:-------------|
| **Arbitrary Code Execution via `eval()`** | Security (Bandit B307, CWE-78) | Line 63 | User input passed directly to `eval()`, allowing arbitrary code execution and system compromise. | Replaced `eval()` with `safe_eval()` using Python's `ast` module to safely parse arithmetic operations without code execution risk. |
| **Bare `except:` Block** | Error Handling (Flake8 E722, Pylint W0702) | Line 44 | Bare `except:` catches all exceptions indiscriminately, including `KeyboardInterrupt` and `SystemExit`, masking critical runtime failures. | Specified concrete exceptions: `except (FileNotFoundError, json.JSONDecodeError, OSError):`. |
| **Mutable Default Argument (`history=[]`)** | Code Smell (Pylint W0102) | Line 12 | Default empty list `history=[]` is created once at function definition and shared across all subsequent invocations, creating unintended side effects. | Replaced default with `history=None` and bound to a dedicated history tracker `READING_HISTORY` when omitted. |
| **Global State Mutation (`global`)** | Design / Maintainability (Pylint W0603) | Lines 27, 40 | Using the `global` statement to mutate `meters` and rate tiers inside functions creates tight coupling and race conditions. | Encapsulated rate tiers in `RATE_TIERS` dictionary and mutated dictionaries in-place; added `get_tier_rates()`. |
| **Resource Leakage & Missing Encoding in File I/O** | Reliability (Pylint R1732, W1514) | Lines 42, 48 | Files opened with bare `open()` without `with` context manager and without explicit UTF-8 encoding, risking unclosed handles. | Refactored file operations to use `with open(file, "r"/"w", encoding="utf-8") as f:`. |
| **Unused Import (`sys`)** | Cleanliness (Flake8 F401, Pylint W0611) | Line 2 | Module `sys` was imported but never utilized in the codebase, bloating namespace. | Removed `import sys`. |
| **Missing Module & Function Docstrings** | Documentation (Pylint C0114, C0116) | Lines 1, 12, 17, 26, 32, 39, 47, 52 | Missing documentation for the module and all functions, violating PEP 257 standards. | Added comprehensive docstrings following Google/PEP 257 docstring style with parameter and return descriptions. |
| **PEP 8 Spacing & Line Length Violations** | Code Style (Flake8 E302, E305, E501) | Lines 12, 17, 24, 26, 32, 39, 47, 52, 62, 68 | Missing 2 blank lines between functions, and multiple lines exceeding the PEP 8 79-character limit. | Reformatted code with proper blank line spacing and wrapped long expressions within 79 characters. |
| **Unnecessary `elif` after `return`** | Refactoring (Pylint R1705) | Line 19 | Using `elif` immediately after a `return` statement adds unnecessary indentation and nesting. | Replaced `elif` with a clean guard-clause `if` structure. |
| **Legacy `%` String Formatting** | Modernization (Pylint C0209) | Lines 59, 60, 66 | Using old C-style `%` string interpolation instead of modern, readable Python f-strings. | Converted all string formatting to modern Python f-strings (`f"{value:.2f}"`). |
| **Negative Consumption Readings (Semantic Bug)** | Functional Logic (Manual Inspection) | Line 55 | `record_reading("M-03", -50)` resulted in a negative total bill (`-192.50`), which is physically impossible for utility consumption. | Added validation warning for negative inputs and clamped bill calculations to non-negative totals (`max(0.0, ...)`). |

---

## 2. Detailed Issue Explanations and Remediations

### 2.1 Bandit Security Fix (High / Medium Severity)
- **Vulnerability:** `record_reading("M-01", eval(adjustment))`
- **Risk:** An attacker entering `__import__('os').system('rm -rf /')` or arbitrary Python expressions could execute arbitrary commands with the privileges of the script runner.
- **Resolution:** Implemented `safe_eval(expr)` using Python's `ast` module. The function parses the expression into an Abstract Syntax Tree (AST) and only permits whitelisted numerical constants (`ast.Constant`) and basic binary arithmetic operators (`ast.Add`, `ast.Sub`, `ast.Mult`, `ast.Div`). Any other nodes raise a `ValueError` and safely return `0.0`.

### 2.2 Flake8 PEP 8 and Exception Handling Fixes
- **Bare Except:** Replaced `except:` with explicit `except (FileNotFoundError, json.JSONDecodeError, OSError):` to prevent swallowing keyboard interrupts or system exit signals.
- **Unused Import:** Removed `import sys`.
- **Formatting:** Standardized top-level definitions to have exactly 2 blank lines before and after function blocks, and wrapped strings/expressions to ensure maximum line length remains $\le 79$ characters.

### 2.3 Pylint Code Quality and Structural Fixes
- **Mutable Default Value:** Altered `def record_reading(meter_id, units, history=[]):` to `def record_reading(meter_id, units, history=None):`. Inside the function, `history` defaults to a dedicated accumulator `READING_HISTORY`.
- **Global Variable Removal:** Replaced `global RATE_TIER_1, ...` with dictionary structure `RATE_TIERS = {"tier_1": 3.5, ...}` which is modified in-place, eliminating all `global-statement` warnings.
- **Context Managers for I/O:** Refactored `load_meter_data` and `save_meter_data` to use `with open(..., encoding="utf-8") as f:`.
- **Docstrings & Clean Returns:** Added module and function-level docstrings, and removed redundant `elif` blocks after `return`.
- **Main Guard:** Added `if __name__ == "__main__": main()` to allow safe import as a reusable module.

---

## 3. Tool Verification Comparison

| Metric / Tool | Before Fixes | After Fixes | Status |
|:---|:---:|:---:|:---:|
| **Pylint Score** | **6.14 / 10** | **10.00 / 10** | ✅ Clean (Target > 9.5 achieved) |
| **Bandit Issues** | 1 Medium (B307) | 0 Issues | ✅ Clean |
| **Flake8 Violations** | 12 Violations | 0 Violations | ✅ Clean |
