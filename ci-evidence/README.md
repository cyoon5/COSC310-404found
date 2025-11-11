CI evidence and artifacts

This folder is intended to contain screenshots and any static artifacts you want to keep in the repository as evidence of CI runs (for grading or documentation).

What the workflow produces
- `reports/` (artifact uploaded by GitHub Actions) contains:
  - `junit.xml` — pytest JUnit-style test results
  - `coverage.xml` — coverage data (Cobertura-style)
  - `htmlcov/` — coverage HTML report (also uploaded as a separate artifact)

How to collect evidence
1. After a CI run, go to the Actions tab in GitHub and open the workflow run.
2. Download the `test-reports` and `coverage-html` artifacts.
3. Save any screenshots or the coverage HTML files into this folder (for grading) and commit them, e.g.:

   git add ci-evidence/your-screenshot.png
   git commit -m "Add CI screenshot evidence"
   git push

You can also include a short text file describing the run (timestamp, branch, summary) if needed.
