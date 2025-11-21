# CodeRabbit Test Samples (Educational)

These files are provided to help you test static analysis and code-review tools like CodeRabbit.

**Included files:**
- vulnerable_app.py — simple Flask + sqlite example that builds SQL by concatenating user input (unsafe pattern).
- vulnerable_queries.sql — example SQL statements showing unsafe assembly patterns (no attack payloads).
- bad_schema.sql — schema file with an intentional syntax error (missing comma) for static analysis detection.
- safe_fix.py — corrected examples showing parameterized queries (best practice).

**Safety & usage notes**
- These samples are for educational/testing purposes only. Do NOT run them against production systems.
- Avoid exposing any test database to external networks. Run locally on a throwaway sqlite DB if needed.
- The files deliberately illustrate insecure coding patterns, but they do NOT contain explicit exploit payloads.

**How to use**
1. Download and unzip the package.
2. Open the folder in VS Code and use the CodeRabbit extension to review files individually (Command Palette → "CodeRabbit: Review File").
3. To simulate a PR-style review, initialize a local git repo, commit a base state, create a feature branch containing the vulnerable files, and run "Review all changes" in CodeRabbit.

