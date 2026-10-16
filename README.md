# Lab 5: Static Code Analysis - Electricity Bill Calculator

**SRN:** PES1UG24CS579

**Date:** 16 October 2026

**Assigned repository:** [SETAPESU26/L5_30_electricity_bill](https://github.com/SETAPESU26/L5_30_electricity_bill)

**Original commit:** `a48c8e9fe56e72e1d809174a23ec2e96a67dd48e`

The program reads sample meter readings from XML, calculates progressive
tariff charges, adds a fixed charge, tax and optional fees, and saves the
result to `bills.json`.

## Results

| Tool | Before | After |
| --- | --- | --- |
| Pylint | 5.44/10 | 10.00/10 |
| Bandit | 4 findings (1 High, 1 Medium, 2 Low) | 0 findings |
| Flake8 | 4 findings | 0 findings |

All 15 regression tests pass. The original demonstration output and saved
bills are unchanged. Each distinct fix has a separate commit; the issue
table lists the corresponding hashes. Baseline evidence and final submission
materials have their own documentation/test commits.

## Setup and run

Verified with Python 3.12.14. From this repository:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python electricity_bill.py
python -m unittest -v
```

`defusedxml` is the runtime dependency. Pylint, Bandit and Flake8 are the lab
analysis tools. Exact installed dependency versions are recorded in
`reports/environment.txt`.

## Reproduce the final analysis

```bash
python -m pylint --persistent=n electricity_bill.py > reports/after/pylint_report.txt 2>&1
python -m bandit -r electricity_bill.py > reports/after/bandit_report.txt 2>&1
python -m flake8 electricity_bill.py > reports/after/flake8_report.txt 2>&1
```

Each command returns zero on the submitted file. Flake8 produces an empty
report when no violations are found. No warnings are suppressed. Preserve
the existing `reports/before` files: they record the unmodified program.

## Deliverables

- [Cleaned program](electricity_bill.py)
- [Issue table with original line numbers and fix commits](issues.md)
- [Reflection draft](reflection.md)
- [Before reports and demo outputs](reports/before)
- [After reports, demo outputs and test results](reports/after)
- [Regression tests](test_electricity_bill.py)

The handout's required minimum of four fixes, Pylint score above 9.5,
resolution of all Bandit findings, and clean Flake8 output are met. The
instructor's exact reflection questions are absent from the supplied
handout; the four reflection sections are explicitly provisional.

The original assignment README remains available in the initial Git commit.
Meter synchronisation is checked with mocked HTTP responses, not a live
device. The supplied sample remains an educational billing demonstration.
