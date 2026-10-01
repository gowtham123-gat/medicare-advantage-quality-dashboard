"""Create documentation and a one-page recruiter summary from computed results."""
from pathlib import Path
import json, sqlite3
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'analysis/results.json').read_text()); O=D['overall'][0]
DISCLAIMER=D['disclaimer']
def pct(v):return f'{v*100:.1f}%'
unattempted=sum(r['Unattempted_Open_Gaps'] for r in D['gaps'])
closure_needed=sum(r['Additional_Closures_To_Target'] for r in D['target'])
findings=[
f"Overall performance leaves a clear backlog. {O['Compliant_Opportunities']:,} of {O['Eligible_Opportunities']:,} eligible member-measure opportunities are compliant ({pct(O['Compliance_Rate'])}), versus a {pct(O['Weighted_Target_Rate'])} eligibility-weighted demonstration target. There are {O['Open_Gaps']:,} open gaps. The aggregate difference is {(O['Compliance_Rate']-O['Weighted_Target_Rate'])*100:.1f} percentage points.",
"Two measures account for most target shortfall. Colorectal Cancer Screening is 57.5% versus a 75.0% target, with 393 open gaps and 162 additional closures needed. Follow-Up After Hospitalization is 53.0% versus 75.0%, with 311 open gaps and 146 additional closures needed. Together they account for 308 of 531 required closures (58.0%). Medication Adherence is above its 85.0% target at 86.9%.",
"Provider Group C needs focused review. Its compliance is 61.2% (728/1,189), compared with 77.5% (1,131/1,459) for Group A, a 16.3 percentage-point difference. Group C has 461 open gaps, 26.9% of the total. These are unadjusted comparisons; check the provider-by-measure matrix before interpreting the overall rank.",
"The South region carries the largest backlog. It has 604 open gaps, 35.3% of all open gaps, and 66.5% compliance (1,200/1,804). The North has 74.4% compliance (1,143/1,536). The 7.9-point difference identifies a region for operational investigation, not a proven cause.",
"Monthly assessed cohorts show an improving trend. Compliance rises from 64.3% in January (657/1,021) to 76.1% in June (754/991), an 11.7-point difference. Each member-measure occurs once in the dataset, so these are different assessed cohorts, not repeated monthly snapshots or proof of a sustained longitudinal intervention effect.",
f"Outreach has both promising channels and an uncovered backlog. Care Coordinator outreach closes 128/193 attempted gaps (66.3%), versus Phone 206/686 (30.0%), SMS 102/408 (25.0%), and Mail 38/353 (10.8%). Overall, 474/1,640 attempted gaps close (28.9%). {unattempted:,} open gaps have no outreach attempt, {unattempted/O['Open_Gaps']*100:.1f}% of the remaining backlog. Channel selection and synthetic generation can explain differences; no causal superiority is established.",
"Data-quality monitoring catches every seeded defect. The separate staging file has 8,020 rows and 66 affected rows (0.82%), including 20 duplicate excess rows, 8 missing member IDs, 8 out-of-cohort ages, 10 conflicting flags, 12 missing outreach channels, and 8 reference-target mismatches. Valid-row rate is 99.18%. The clean 8,000-row file passes the same ten rules with zero detected violations. The clean file is the original synthetic reference, not evidence of an automated staging repair process."
]
recommendations=[
"Prioritize Colorectal Cancer Screening and Follow-Up After Hospitalization. Build measure-specific worklists and review unresolved gaps weekly. Use 162 and 146 additional closures as arithmetic planning targets with the current denominators held fixed; these are not forecasts or promised outcomes.",
"Review Provider Group C and the South region with operations staff. Compare the same measure and month, confirm gap evidence, and investigate scheduling or outreach barriers before assigning performance causes. Track open gaps, numerator, denominator, and variance to target.",
"Address the 545 unattempted open gaps. Start with gaps in the two highest-shortfall measures, assign an outreach owner, and track attempted, reached, and closed counts separately. A zero attempt must not be mistaken for an unsuccessful contact.",
"Pilot a channel escalation workflow. Keep SMS/phone for routine outreach and evaluate coordinator follow-up for selected unresolved gaps. Compare similar populations and capture cost and time before deciding whether the higher observed coordinator closure rate justifies broader use.",
"Run data-quality checks before every refresh. Quarantine unresolved errors, retain the staging source and audit row numbers, and reconcile clean counts with SQL and Power BI. Maintain reference targets separately and obtain approved specifications before any real operational use."
]
md='# Analysis findings and recommendations\n\n'+DISCLAIMER+'\n\n## Findings\n\n'+ '\n\n'.join(f'{i+1}. {f}' for i,f in enumerate(findings))+'\n\n## Recommendations\n\n'+'\n\n'.join(f'{i+1}. {f}' for i,f in enumerate(recommendations))
md+='\n\n## Interpretation limits\n\nTargets, eligibility and channel probabilities are demonstration assumptions. Diabetes Care is a broad synthetic indicator, Medication Adherence is not a drug-class-specific PDC calculation, and Follow-Up After Hospitalization is not a replicated official measure. There are no clinical event dates, claims, pharmacy fills, enrollment periods, exclusions or audited source records. This project does not calculate CMS Stars or certified HEDIS measures. No real savings, quality improvement, patient outcome or employer result is claimed. See data_dictionary.md for the exact definitions.\n'
(ROOT/'analysis/findings_and_recommendations.md').write_text(md)
portfolio=f'''# Medicare Advantage Quality Improvement Dashboard

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

**Synthetic-data disclaimer:** {DISCLAIMER}

**Portfolio card text:** An interactive case study using 8,000 synthetic healthcare quality records to analyze compliance, care gaps, outreach, and data quality. Includes SQL, Excel, and a Power BI build guide.

**Suggested buttons:** View dashboard · Download project summary · Download dataset and SQL

**Website integration:** Add this as a new project card on your existing Data Analyst portfolio. Use `dashboard_cover.png` as the cover image. Host `dashboard_preview.html` as a standalone static page and link to it; it embeds synthetic records and needs no backend. Upload the recruiter summary PDF and project ZIP and connect the download buttons. If your website supports an iframe, embed the hosted HTML page with a descriptive title and allow enough height for tables. Complete the Desktop guide before adding a screenshot labeled as a Power BI report.
'''
(ROOT/'portfolio/website_content.md').write_text(portfolio)

dictionary='''# Data dictionary and analytical definitions

This project uses entirely synthetic data created for demonstration purposes. No PHI, PII, patient records, or proprietary employer data are included.

## Grain and scope

The clean dataset has 8,000 unique member-measure records across 3,075 represented synthetic members, January-June 2026. One member can have multiple measures, but a member-measure pair appears once in the whole dataset. Members were sampled from a generated 3,200-member pool. Each member has one assigned assessment month, region and provider group. The composite key is Member_ID + Measure_Name. Month is an assessment bucket; ISO dates use the first day for sorting, not an actual service date.

Compliance is status at the end of the assessment month. Outreach fields describe the recorded outreach episode during that month; attempts are cumulative for that episode. Pre-existing compliant members and ineligible records have no outreach episode. No repeated snapshots, churn, reopened gaps or subsequent follow-up are modeled.

| Field | Type | Meaning and allowed values |
| --- | --- | --- |
| Member_ID | Text | Generated SYN00001-style label. No real identifier. |
| Age | Integer | Synthetic age 65-89 at assessment; not a complete representation of Medicare eligibility. |
| Gender | Text | Female or Male, simplified synthetic categories used by the demonstration eligibility rule. Not a clinical eligibility engine. |
| Region | Text | North, South, East, West; generic simulated regions, not Alignment Health markets. |
| Provider_Group | Text | Provider Group A-E; fictional groups. |
| Measure_Name | Text | Six broad demonstration quality indicators listed below. |
| Eligible_Flag | Integer | 1 included in the demonstration denominator; 0 excluded. |
| Compliant_Flag | Integer | 1 meets the simulated indicator at assessment month end; 0 does not. Always 0 when ineligible. |
| Gap_Status | Text | Open if eligible and noncompliant; Compliant if eligible and compliant; Not Eligible otherwise. A compliant status does not necessarily mean a new closure. |
| Measurement_Month | Date | First day of assessment month, 2026-01-01 through 2026-06-01. |
| Outreach_Attempts | Integer | 0-4 attempts in the recorded episode. Not a unique-member count. |
| Outreach_Channel | Text | Phone, SMS, Mail, Care Coordinator, or None when no attempt. One assigned channel per episode. |
| Outreach_Status | Text | Reached, Unable to Reach, Declined for attempted gaps; Not Attempted for open gaps with zero attempts; Not Needed for pre-existing compliant/ineligible records. |
| Gap_Closed | Integer | 1 if an initially open eligible gap closed during the recorded outreach episode; 0 otherwise. Closure requires Reached, positive attempts and Compliant_Flag=1. |
| Target_Rate | Decimal | 0-1 demonstration planning target, constant by measure. Not a CMS cut point. |

## Measure assumptions

| Measure | Demonstration target | Simplified eligibility and simulated numerator |
| --- | --- | --- |
| Controlling Blood Pressure | 80% | Random synthetic hypertension-indicator eligibility within ages 65-89. Binary simulated control; no observed BP readings. |
| Colorectal Cancer Screening | 75% | Ages 65-75, with an additional randomly simulated eligibility exclusion. Binary screening completion, no modality or lookback evidence. |
| Breast Cancer Screening | 80% | Female category and ages 65-74, with randomly simulated eligibility exclusion. Binary screening completion, no clinical anatomy or exclusion logic. |
| Diabetes Care | 78% | Random synthetic diabetes-indicator eligibility. Binary completion of a fictional diabetes care requirement; not a specific A1c or composite specification. |
| Medication Adherence | 85% | Random synthetic medication-indicator eligibility. Binary simulated adherence, not PDC, refill history or an official drug-class measure. |
| Follow-Up After Hospitalization | 75% | Random synthetic hospitalization-indicator eligibility. Binary simulated follow-up, no diagnosis, discharge date or 7/30-day official timing rule. |

All rules above are authored demonstration assumptions. No approved clinical specification or real quality-measure certification is implied.

## Metric definitions

| Metric | Numerator | Denominator or formula |
| --- | --- | --- |
| Compliance rate | Eligible and compliant opportunities | All eligible opportunities in filter context |
| Open gaps | Eligible and noncompliant opportunities | Count, not rate; can exceed unique members |
| Weighted target | Sum of target for every eligible record | Number of eligible records |
| Variance pp | Compliance rate minus weighted target | Multiply fraction difference by 100 |
| Additional closures | Per-measure max(0, ceiling(eligible x target) minus compliant) | Sum each measure's nonnegative shortfall; no cross-measure offset |
| Starting gaps | Open at end or Gap_Closed=1 | Count of initially open opportunities |
| Outreach coverage | Attempted starting gaps | All starting gaps |
| Reach rate | Attempted gaps with Reached status | All attempted gaps |
| Outreach closure rate | Closed gaps | All attempted gaps |
| Closure among reached | Closed gaps | Reached attempted gaps |
| Valid row rate | Staging rows with zero failed checks | All staging rows |
| Issue row rate | Staging rows with one or more failed checks | All staging rows |

Never average subgroup percentages to get the overall compliance rate. Divide the summed numerator by the summed eligible denominator. Distinct member counts are not additive across measures. Monthly cohorts differ; rates are descriptive, not longitudinal outcomes. Provider/region rates are unadjusted. Channel rates describe simulated associations, not causal effects.

## Reproducibility and staging defects

`scripts/generate_project.py` uses Python's standard random generator with seed 20260930. Measure, provider, region and month differences are intentionally embedded in generation probabilities. The staging file is a modified copy with 46 affected original records and 20 appended duplicate records. The unmodified clean file is the synthetic reference. Error detection does not automatically repair, infer or impute corrupted values.

`dq_audit.csv`: Row_ID (1-based staging data-row number), Member_ID, Region, Provider_Group, Measure_Name, Measurement_Month, Issue_Count, DQ_Status. `dq_errors.csv`: Row_ID, Rule_ID, Rule_Name. Row_ID supports traceability to the staging file. It is not a member identifier. Multiple failed rules per row are supported even though this seeded version has one failure per affected row.
'''
(ROOT/'data/data_dictionary.md').write_text(dictionary)

readme='''# Medicare Advantage Quality Improvement Dashboard

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
'''
(ROOT/'README.md').write_text(readme)
(ROOT/'sql/04_run_analysis.sql').write_text('''-- Query the supplied database; no schema recreation required.
SELECT * FROM v_overall;
SELECT * FROM v_measure_performance ORDER BY Compliance_Rate;
SELECT * FROM v_provider_performance ORDER BY Compliance_Rate;
SELECT * FROM v_provider_measure ORDER BY Measure_Name,Compliance_Rate;
SELECT * FROM v_region_performance ORDER BY Open_Gaps DESC;
SELECT * FROM v_care_gaps ORDER BY Open_Gaps DESC;
SELECT * FROM v_monthly_trend;
SELECT * FROM v_outreach_effectiveness ORDER BY Closure_Rate DESC;
SELECT * FROM v_target_opportunity;
SELECT Rule_ID,Rule_Name,COUNT(*) AS Violations FROM dq_errors GROUP BY Rule_ID,Rule_Name;
SELECT * FROM dq_audit WHERE Issue_Count>0 ORDER BY Row_ID;
''')

title='Medicare Advantage Quality Improvement Dashboard'
intro='Independent portfolio case study using synthetic healthcare quality records to identify improvement priorities, compare outreach results, and monitor data reliability.'
sections=[
('Business question','Where should a quality improvement team focus follow-up when measure performance varies across providers and regions?'),
('Scope and method','Created 8,000 member-measure records representing 3,075 synthetic members assessed during January-June 2026. Used SQL to calculate eligible-denominator rates, target shortfalls, monthly cohort trends and outreach results. Kept a separate staging dataset for ten audit rules.'),
('Selected findings','Overall compliance is 70.9% (4,173/5,884), with 1,711 open gaps. Colorectal screening and post-hospital follow-up account for 308 of 531 additional closures needed to meet all demonstration targets. Provider Group C is at 61.2% versus Group A at 77.5%. A further 545 open gaps have no outreach attempt.'),
('Recommended actions','Prioritize the two highest-shortfall measures, review Provider Group C and the South region within each measure, work the unattempted backlog, and test coordinator escalation for unresolved gaps. Validate source records before each refresh.'),
('Delivered work','SQL queries and a ready-to-query SQLite database, an Excel analysis workbook, a working four-page browser dashboard, a data dictionary, seven findings and five recommendations. Power BI deliverables include DAX, model relationships, a theme and exact visual mappings for all four pages. Native Power BI Desktop implementation remains the final build step.'),
('Demonstrated value','Shows practical analyst skills in metric definition, SQL, reporting, data validation and translating findings into operational priorities. The 531-closure opportunity is an arithmetic planning estimate, not a realized healthcare or financial result.'),
('Interpretation','Targets and eligibility rules are demonstration assumptions. Monthly cohorts differ. Channel results are descriptive. This project does not calculate official CMS Stars or certified HEDIS measures.')]
doc=Document();sec=doc.sections[0];sec.top_margin=Inches(.55);sec.bottom_margin=Inches(.5);sec.left_margin=sec.right_margin=Inches(.68)
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
for name in ['Normal','Title','Subtitle','Heading 1']:
    st=doc.styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
for style in doc.styles:
    for node in list(style.element.iter(qn('w:pBdr'))):
        node.getparent().remove(node)
doc.styles['Normal'].font.size=Pt(10)
doc.styles['Normal'].paragraph_format.space_after=Pt(5)
doc.styles['Normal'].paragraph_format.line_spacing=1.04
doc.styles['Title'].font.size=Pt(22);doc.styles['Title'].paragraph_format.space_after=Pt(6)
doc.styles['Heading 1'].font.size=Pt(11);doc.styles['Heading 1'].paragraph_format.space_before=Pt(7);doc.styles['Heading 1'].paragraph_format.space_after=Pt(3)
doc.add_paragraph(title,'Title');doc.add_paragraph(intro)
for heading,body in sections:doc.add_paragraph(heading,'Heading 1');doc.add_paragraph(body)
p=doc.add_paragraph(DISCLAIMER);p.runs[0].bold=True;p.runs[0].font.size=Pt(9)
doc.core_properties.title=title;doc.core_properties.author='';doc.core_properties.subject='Synthetic healthcare analytics portfolio case study'
doc.save(ROOT/'summary/Recruiter_Project_Summary.docx')

pdfmetrics.registerFont(TTFont('ProjectFont','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('ProjectBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ProjectTitle',fontName='ProjectBold',fontSize=21,leading=24,spaceAfter=10,textColor=colors.HexColor('#14243B')))
styles.add(ParagraphStyle(name='ProjectBody',fontName='ProjectFont',fontSize=9.8,leading=13,spaceAfter=6,textColor=colors.HexColor('#253449')))
styles.add(ParagraphStyle(name='ProjectHead',fontName='ProjectBold',fontSize=10.4,leading=13,spaceBefore=6,spaceAfter=3,textColor=colors.HexColor('#14243B')))
story=[Paragraph(title,styles['ProjectTitle']),Paragraph(intro,styles['ProjectBody']),Spacer(1,6)]
for h,b in sections:story.extend([Paragraph(h,styles['ProjectHead']),Paragraph(b,styles['ProjectBody'])])
story.extend([Spacer(1,5),Paragraph(DISCLAIMER,ParagraphStyle(name='Disclaimer',fontName='ProjectBold',fontSize=8.7,leading=11,textColor=colors.HexColor('#253449')))])
SimpleDocTemplate(str(ROOT/'summary/Recruiter_Project_Summary.pdf'),pagesize=(612,792),leftMargin=42,rightMargin=42,topMargin=35,bottomMargin=32,title=title,author='').build(story)
print('Documentation, portfolio copy, DOCX and PDF created.')
