# Lab 5: Static Code Analysis — Energy Consumption & Tariff Calculator

**Your file:** `energy_system.py`

Follow the lab handout for the full instructions.

## About the program

A utility meter tracker. It records meter readings, computes a three-tier electricity bill, flags meters with unusually high usage and stores readings in `meters.json`.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Run it first** and read the output carefully:
   ```bash
   python energy_system.py
   ```
   It asks one question. Press Enter to use the default, then try a few inputs of your own. Not every problem in this file is something a tool will flag, so pay attention to output that looks wrong.

2. **Install the tools:**
   ```bash
   pip install pylint bandit flake8
   ```

3. **Run the analysis** and save the reports:
   ```bash
   pylint energy_system.py > pylint_report.txt
   bandit -r energy_system.py > bandit_report.txt
   flake8 energy_system.py > flake8_report.txt
   ```

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   |-------|------|---------|-------------|--------------|
   | ... | ... | ... | ... | ... |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

## Deliverables

1. `energy_system.py`: your cleaned version, with at least 4 issues fixed.
2. `issues.md`: the completed issue table.
3. `reflection.md`: your answers to the reflection questions.

**Target:** aim for a Pylint score above 9.5 on your final file. A perfect 10.00/10 is very good.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.

---

## How to run (final version)

```bash
pip install pylint bandit flake8
python energy_system.py          # press Enter (or type e.g. 50*2+3) at the prompt
```

The expression prompt is evaluated with a safe AST-based parser (`safe_eval`), not `eval()`. Invalid input counts as 0 units. Readings are saved to `meters.json` (git-ignored).

## How to run the analysis

```bash
pylint energy_system.py > pylint_report.txt
bandit -r energy_system.py > bandit_report.txt
flake8 energy_system.py > flake8_report.txt
```

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.14/10 (`pylint_report_before.txt`) | 10.00/10 (`pylint_report_after.txt`) |
| Bandit | 1 Medium issue, B307 `eval` (`bandit_report_before.txt`) | 0 issues (`bandit_report_after.txt`) |
| Flake8 | 12 violations (`flake8_report_before.txt`) | 0 violations (`flake8_report_after.txt`) |

Fixes were committed per tool (Bandit, Flake8, Pylint). See `issues.md` for the issue table and `reflection.md` for the reflection answers.
