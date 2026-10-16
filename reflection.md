# Reflection

PES1UG24CS579 | Lab 5 | 16 October 2026

The supplied three-page handout refers to reflection questions but does not
list them. The assigned README requests four answers. The following four
sections are provisional reflections on the completed work, not a claim to
reproduce the missing questions. Align them with the instructor's exact
questions when those are available.

## 1. What each tool contributed

Pylint identified naming and documentation problems, the mutable default
dictionary, an unused argument and an unspecified file encoding. Bandit
identified the shell call, insecure XML parsing and the hard-coded demo
password. Flake8 identified four formatting violations. The tools overlap
in some areas but provide different views of the same program. Using all
three made the review more thorough than relying on the Pylint score alone.

## 2. How the issues were prioritised

The highest-priority finding was B605 because the meter address was inserted
directly into a shell command. The replacement validates an IP address and
makes the request without a shell. The medium-severity XML finding was
addressed next by switching to a hardened parser and rejecting DTDs. The
remaining Bandit findings, Pylint warnings and conventions, and Flake8
formatting issues followed. Individual commits make each change traceable.

## 3. What demonstrated that the fixes worked

Pylint improved from 5.44 to 10.00, Bandit findings decreased from four to
zero, and Flake8 findings decreased from four to zero. These results were
checked against the final saved reports. More importantly, the demonstration
output and JSON file remained byte-for-byte identical to the original.
Fifteen tests cover tariff boundaries, tax and fees, parsing, file output,
import safety and mocked meter communication. No live meter was available,
so the tests establish the helper's request and error-handling behaviour,
not interoperability with a physical meter.

## 4. Limits of static analysis and lessons for future work

A tool warning needs interpretation. The shared default dictionary was a
latent problem, even though this version did not mutate it. Conversely, the
import-time demonstration was a real side effect found during manual review,
not by the three reports. A perfect Pylint score and a clean Bandit scan do
not prove correct tariffs, secure deployment or complete input validation.
Future changes should combine static analysis with focused tests and review
of requirements. Production use would also require approved tariff rules,
clear validation policies, controlled meter access and appropriate transport
security.
