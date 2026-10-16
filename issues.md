# Identified issues and fixes

PES1UG24CS579 | Lab 5 | 16 October 2026

Original line numbers refer to `electricity_bill.py` at upstream commit
`a48c8e9fe56e72e1d809174a23ec2e96a67dd48e`. Bandit severities are copied from
the actual before report; Pylint and Flake8 categories are not assigned
invented security severities. Each row has its own fix commit.

| Issue | Type | Line(s) | Description | Fix Approach |
| --- | --- | --- | --- | --- |
| B605: shell command injection | Security - High | 63 | A caller-controlled meter address is concatenated into a shell command. Shell metacharacters could execute additional commands. | Replace the shell with `HTTPConnection`, validate a literal IP, use a fixed `/reading` path, apply a five-second timeout and close the connection in `finally`. Commit `ee262bf`. |
| B314 / B405: unsafe XML parsing | Security - Medium call / Low import | 3, 18 | The standard XML parser is used without the hardening recommended by Bandit for potentially untrusted XML. The supplied sample itself is benign. | Use `defusedxml.ElementTree.fromstring` with DTDs forbidden; reject entity-based payloads. Commit `e7633f8`. |
| B105: hard-coded password | Security - Low | 13 | An unused demo password is embedded in source. No authentication consumes it. | Remove the unused constant instead of retaining an unnecessary credential. Commit `e29ce49`. |
| C0114 / C0116: missing documentation | Pylint - Convention | 1, 17, 22, 29, 42, 50, 56, 61, 66 | The module and functions have no docstrings explaining their responsibilities. | Add concise module and function docstrings. Commit `7cf47a1`. |
| C0103: inconsistent naming | Pylint - Convention | 17, 22, 29, 34, 42, 50, 56, 61, 67 | Functions, arguments and a local variable use camelCase instead of Python's snake_case convention. | Rename them and update every internal call site. Commit `5e62a71`. |
| W0102: mutable default argument | Pylint - Warning | 42 | `extras={}` creates a shared dictionary default. The original function only reads it, so this is a latent risk rather than demonstrated cross-call mutation. | Use `extras=None` and create a new dictionary inside the function. Commit `8eca911`. |
| W0613: unused argument | Pylint - Warning | 50 | `currency` is accepted but ignored, suggesting unsupported conversion behaviour. | Remove the argument and update the caller; bills remain denominated in rupees. Commit `6effe7d`. |
| W1514: unspecified encoding | Pylint - Warning | 57 | JSON output relies on the platform's default text encoding. | Explicitly use UTF-8 when opening the output file. Commit `2738b92`. |
| E302: insufficient blank lines | Flake8 - Style | 22 | A top-level function has only one preceding blank line. | Add the second blank line. Commit `a364ba3`. |
| E203: whitespace before colon | Flake8 - Style | 44 | A dictionary key has an unnecessary space before its colon. | Remove that space. Commit `2581a11`. |
| E501: overlong line | Flake8 - Style | 72 | A print statement has 86 characters, exceeding the default 79-character limit. | Wrap the argument list without changing the printed output. Commit `67e6e9b`. |
| E225: operator spacing | Flake8 - Style | 76 | Assignment lacks the expected surrounding spaces. | Change `total=...` to `total = ...`. Commit `13fbf2f`. |
| Import-time execution | Manual review - Side effect | 82 | Importing the module executes the demonstration, prints output and writes `bills.json`. This was not reported by the three tools. | Add a `__main__` guard so imports are safe for reuse and testing. Commit `0898e7c`. |

## Verified results

| Check | Before | After |
| --- | --- | --- |
| Pylint | 5.44/10; 26 messages | 10.00/10; no messages |
| Bandit | 4 findings: 1 High, 1 Medium, 2 Low | 0 findings |
| Flake8 | 4 findings | 0 findings |
| Regression tests | No supplied suite | 15 tests pass |

The final demonstration stdout and generated JSON match the original saved
outputs byte for byte. The amounts are 708.75, 2661.75, 78.75 and 288.75;
the highest bill belongs to M2, the average is 934.5 and the total is 3738.0.

The final analysis targets `electricity_bill.py`, as the assignment requires.
No checker rules were disabled and no `nosec` or `noqa` comments were added.
The empty final Flake8 report is the tool's normal successful output.

## Scope of verification

Tests cover slab boundaries, reversed readings, fees, tax, JSON persistence,
malicious XML rejection, import behaviour and mocked meter HTTP requests.
No real meter was contacted. The helper retains the original HTTP protocol;
it now accepts literal IPv4/IPv6 addresses and returns decoded reading text
instead of letting `curl` print it. HTTP status failures and timeouts propagate
to the caller after connection cleanup. This demo is not a complete production
billing or authentication system; a clean scan does not establish that it is.
