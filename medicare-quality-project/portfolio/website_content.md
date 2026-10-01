# Medicare Advantage Quality Improvement Dashboard

**Project subtitle:** A synthetic healthcare analytics case study for tracking quality performance, prioritizing care gaps, and evaluating outreach.

**Business problem:** Quality improvement teams need a consistent view of measure performance, provider variation, open care gaps, and outreach activity to decide where to focus follow-up.

**Solution:** Built an 8,000-record synthetic dataset and used SQL to calculate denominator-based rates, monthly trends, target shortfalls, and outreach results. Created a working four-page browser dashboard, an Excel analysis workbook, and a Power BI implementation guide with DAX and exact visual mappings. A separate staging dataset demonstrates ten data-quality rules.

**Tools used:** SQL (SQLite), Python, Excel, HTML/CSS/JavaScript. Power BI report design and DAX definitions are included for implementation in Power BI Desktop.

**Key findings:**

- 70.9% compliance across 5,884 eligible opportunities, with 1,711 open gaps.
- Colorectal screening and post-hospital follow-up account for 58.0% of required closures to the demonstration targets.
- 545 open gaps have no outreach attempt; coordinator outreach has the highest observed closure rate in the simulated data.
- The audit identifies 66 affected rows in a separate staging dataset.

**Business impact:** Demonstrates how an analyst can turn quality data into measure-specific priorities, provider review lists, outreach worklists, and refresh checks. Identifies 531 additional closures needed to meet every measure's demonstration target, holding denominators fixed. This is a planning opportunity in simulated data, not a realized patient or financial outcome.

**Synthetic-data disclaimer:** This project uses entirely synthetic data created for demonstration purposes. No PHI, PII, patient records, or proprietary employer data are included.

**Portfolio card text:** An interactive case study using 8,000 synthetic healthcare quality records to analyze compliance, care gaps, outreach, and data quality. Includes SQL, Excel, and a Power BI build guide.

**Suggested buttons:** View dashboard · Download project summary · Download dataset and SQL

**Website integration:** Add this as a new project card on your existing Data Analyst portfolio. Use `dashboard_cover.png` as the cover image. Host `dashboard_preview.html` as a standalone static page and link to it; it embeds synthetic records and needs no backend. Upload the recruiter summary PDF and project ZIP and connect the download buttons. If your website supports an iframe, embed the hosted HTML page with a descriptive title and allow enough height for tables. Complete the Desktop guide before adding a screenshot labeled as a Power BI report.
