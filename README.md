# Medicare Advantage Quality Improvement Dashboard

This project uses entirely synthetic data created for demonstration purposes. No PHI, PII, patient records, or proprietary employer data are included.

An independent portfolio case study demonstrating SQL analysis, denominator-based healthcare quality metrics, outreach worklists, data-quality monitoring, Excel reporting and Power BI report design. It is designed to support a Data Analyst interview discussion. It is not an Alignment Health deliverable or an official CMS/HEDIS calculation.

## Start here

1. Open `portfolio/dashboard_preview.html` in any modern desktop browser. It runs offline with embedded synthetic data, four report pages, common filters and an outreach-channel filter.
2. Review `summary/Recruiter_Project_Summary.pdf` for the one-page overview. An editable DOCX is also supplied.
3. Open `Medicare_Quality_Analysis.xlsx` for the raw data and formula-based measure, provider, monthly and outreach summaries.
4. Follow `powerbi/dashboard_specification.md` to implement the native Power BI report. Paste DAX definitions one at a time. A `.pbix` is not included and the DAX/visuals have not been executed in Power BI Desktop.
5. Use `portfolio/website_content.md` and `portfolio/dashboard_cover.png` for your existing portfolio project card. Host the standalone HTML preview and link the PDF and project ZIP. No existing website has been modified.

## Files

| Path | Purpose |
| --- | --- |
| data/medicare_quality_synthetic.csv | Clean canonical 8,000-record synthetic dataset |
| data/medicare_quality_staging.csv | 8,020-record source with seeded defects for audit demonstration |
| data/dq_audit.csv and dq_errors.csv | SQL-generated audit outputs for Power BI Page 4 |
| data/data_dictionary.md | Grain, column definitions, targets, and interpretation limits |
| data/medicare_quality.db | Ready-to-query SQLite database containing clean and staging data, targets, analysis views and DQ views |
| sql/01_schema.sql | SQLite schema and indexes |
| sql/02_analysis_queries.sql | Measure/provider/region performance, gaps, trends, outreach and target opportunity |
| sql/03_data_quality_checks.sql | Ten check rules, audit views and diagnostic queries |
| sql/04_run_analysis.sql | SELECT statements for all analysis outputs |
| powerbi/model_and_measures.dax | Tables and all measures used in the four-page specification |
| powerbi/dashboard_specification.md | Import, types, relationships, exact visual wells, filters, slicers and acceptance checks |
| powerbi/theme.json | Optional Power BI theme |
| analysis/findings_and_recommendations.md | Seven findings, five recommendations and limits |
| analysis/*.csv and results.json | Reproducible analysis results |
| analysis/validation_report.txt | Executed checks and Desktop validation boundary |
| portfolio/dashboard_preview.html | Working standalone browser dashboard, not a native Power BI export |
| summary/Recruiter_Project_Summary.pdf and .docx | One-page recruiter sample |
| scripts/generate_project.py | Standard-library-only deterministic generator and SQL verification |
| scripts/create_content.py | Rebuild documentation and summaries; requires python-docx and reportlab |

## Query the database

Use SQLite 3.25+ in DB Browser for SQLite, a SQLite extension, or the command-line client:

```bash
sqlite3 data/medicare_quality.db < sql/04_run_analysis.sql
```

The supplied database is already loaded. Do not rerun CREATE TABLE/VIEW scripts against it. To build a fresh database and CSV/audit outputs, run from the project directory:

```bash
python scripts/generate_project.py
```

This uses only Python's standard library and replaces the generated CSVs, database and analysis files. On Python 3.11 the seed reproduces the supplied output. SQL syntax is SQLite, not T-SQL; import dates as ISO text when reproducing in SQLite. To use another SQL engine, adapt date, boolean, window and ceiling syntax while preserving metric definitions.

## Verified baseline

8,000 records; 3,075 members; 5,884 eligible opportunities; 4,173 compliant; 70.9% compliance; 1,711 open gaps; 79.5% weighted demonstration target. Five measures are below target, requiring 531 additional closures across measures with fixed denominators. Outreach: 1,640 attempted gaps, 474 closures, 28.9% closure rate. Staging: 8,020 rows, 66 affected, 20 duplicate excess rows, 99.18% valid.

SQL counts, source flags and audit rules were executed and reconciled. Excel formulas and charts were recalculated and visually inspected. The dashboard's JavaScript calculations and filter handlers were checked with a minimal DOM fixture. A browser executable was unavailable, so browser layout was not visually tested. Power BI Desktop has not been run in this environment; finish the guide's acceptance checks before presenting a native Power BI dashboard as completed.

`scripts/build_browser_dashboard.py` rebuilds the standalone HTML with the standard library. `scripts/check_dashboard.mjs` runs JavaScript calculation and filter checks with Node.js. `scripts/create_cover.py` rebuilds the static portfolio cover with Matplotlib. `scripts/build_workbook.mjs` requires the Codex artifact spreadsheet runtime and is included as the Excel authoring source; it is not required to use the delivered workbook. The final recruiter PDF is a visually verified export of the supplied DOCX.

## Limits and interview discussion

Every quality measure is a simplified simulated indicator. Targets are authored assumptions, not CMS cut points. No Stars, certified HEDIS scores, clinical advice or realized financial impact are calculated. Monthly observations are different cohorts, not repeated snapshots. Outreach channel comparisons are not causal. Provider rates are not risk-adjusted. The clean file is the original synthetic reference rather than a staging-cleaning output.

Explain the denominator, composite key, open-versus-newly-closed gap distinction, the ceiling calculation by measure, and the reason raw audit results are kept apart from clean performance metrics. Present the recommendations as proposed operational actions, not work implemented for an employer.

## Reference documentation

- Microsoft DAX CALCULATE: https://learn.microsoft.com/en-us/dax/calculate-function-dax
- Microsoft DAX DIVIDE: https://learn.microsoft.com/en-us/dax/divide-function-dax
- Microsoft date tables: https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables
- Official CMS rating resources: https://www.cms.gov/medicare/health-drug-plans/part-c-d-performance-data

These sources informed terminology and model patterns. No clinical or employer data was imported from them.
