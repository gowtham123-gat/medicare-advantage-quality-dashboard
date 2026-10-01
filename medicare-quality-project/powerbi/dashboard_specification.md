# Medicare Advantage Quality Improvement Dashboard

This is an implementation specification for a four-page Power BI report. The included browser dashboard is a working preview; a native `.pbix` has not been created or executed in Power BI Desktop.

This project uses entirely synthetic data created for demonstration purposes. No PHI, PII, patient records, or proprietary employer data are included.

## 1. Import and model

1. Open Power BI Desktop. Get data > Text/CSV > `data/medicare_quality_synthetic.csv` > Transform data. Rename query `FactQuality`.
2. Import `data/dq_audit.csv` as `DQAudit` and `data/dq_errors.csv` as `DQErrors`.
3. Remove automatic Changed Type steps if they inferred wrong types. For FactQuality, use Whole number for Age, Eligible_Flag, Compliant_Flag, Outreach_Attempts, Gap_Closed; Decimal number for Target_Rate; Date for Measurement_Month; Text for all remaining fields. DQAudit: Row_ID and Issue_Count Whole number, Measurement_Month Date, other columns Text. DQErrors: Row_ID Whole number, Rule_ID and Rule_Name Text. Close & Apply.
4. Copy each calculated-table definition from `model_and_measures.dax` using Modeling > New table. Copy each measure separately using New measure. The file is a reference of definitions, not a batch paste script.
5. Create the relationships below. Use active, single-direction filtering from the left table to the right table. Remove any automatically detected fact-to-fact relationships.

| From column | To column | Cardinality |
| --- | --- | --- |
| DimDate[Date] | FactQuality[Measurement_Month] | One to many |
| DimDate[Date] | DQAudit[Measurement_Month] | One to many |
| DimMeasure[Measure_Name] | FactQuality[Measure_Name] | One to many |
| DimMeasure[Measure_Name] | DQAudit[Measure_Name] | One to many |
| DimProvider[Provider_Group] | FactQuality[Provider_Group] | One to many |
| DimProvider[Provider_Group] | DQAudit[Provider_Group] | One to many |
| DimRegion[Region] | FactQuality[Region] | One to many |
| DimRegion[Region] | DQAudit[Region] | One to many |
| DQAudit[Row_ID] | DQErrors[Row_ID] | One to many |
| DQRule[Rule_ID] | DQErrors[Rule_ID] | One to many |

6. Mark DimDate as the date table using Date. Sort YearMonth by YearMonthSort. Disable automatic date/time for this report. Use YearMonth rather than an automatically generated date hierarchy.
7. Hide fact copies of Region, Provider_Group, Measure_Name and Measurement_Month from report view so slicers use dimensions. Hide all source numeric flags and Target_Rate from report view; use explicit measures. Keep IDs accessible only for detail tables. Set remaining identifiers to Don't summarize.
8. Import `theme.json` through View > Themes > Browse for themes. Format counts `#,0`, rates `0.0%`, pp measures `0.0` (include `pp` in visual titles), rank whole number, average attempts `0.00`.

DQAudit is a row-level result of the SQL checks against the staging file. DQErrors contains one row per failed rule. If staging changes, rerun SQL or `scripts/generate_project.py` and refresh both audit CSVs. DAX does not revalidate the raw staging CSV automatically.

## 2. Shared behavior and layout

- Canvas: 16:9, 1280 x 720. White panels on #F3F6FA, dark navy labels, blue performance, green target, amber open gaps. Every page contains the report title, page title and a small synthetic-data note.
- Common slicers on every page: `DimDate[YearMonth]`, `DimRegion[Region]`, `DimProvider[Provider_Group]`, `DimMeasure[Measure_Name]`. Dropdown, multi-select, Select all on; initial state All. Sync these four slicers across all pages. They filter all data visuals on their page.
- No report-wide eligibility filter. Eligibility is handled by the measures. No page-wide Compliant_Flag, Gap_Status, outreach status, or channel filter.
- Page 3 additionally has `FactQuality[Outreach_Channel]`, initial All, unsynced. It filters all Page 3 visuals. Selecting a channel restricts analysis to that channel, so coverage in such a slice will be 100% for actual channels. Keep All for backlog triage.
- Page 4 has no outreach slicer: raw defects should not disappear through clean-fact selections. Common dimension slicers still filter DQAudit and through it DQErrors.
- All measures return blank rates for a zero denominator. Show blanks as `No eligible records` in tooltip text, not a fabricated 0%.
- Default chart interactions: cross-filter within page. Disable interactions from care-gap detail table to all other visuals. On Page 4 disable the rule bar's effect on cards, monthly chart and provider matrix; enable its effect on the error detail table only. This keeps row counts distinct from rule-violation counts.
- Tooltips for performance charts: Eligible Opportunities, Compliant Opportunities, Compliance Rate, Weighted Target Rate, Variance pp, Open Gaps. Outreach tooltips: Attempted Gaps, Reached Gaps, Closed Gaps, Reach Rate, Outreach Closure Rate.

## 3. Exact visual field assignments

In the tables below, `—` means no field/slot is used. `Common` means the four dimension slicers above apply. All visual-specific filters supplement the common slicers. Numeric visual filters are evaluated after slicers. Put measures in Values, not implicit aggregations of flags. Position descriptions define the reading order; leave padding between panels.

### Page 1 Executive Quality Overview

| ID and visual | X-axis | Y-axis | Values or additional wells | Legend | Visual filters and sort | Slicers |
| --- | --- | --- | --- | --- | --- | --- |
| E1 Card, top left | — | — | Unique Members | — | None | Common |
| E2 Card, top row | — | — | Eligible Opportunities | — | None | Common |
| E3 Card, top row | — | — | Compliance Rate | — | None | Common |
| E4 Card, top row | — | — | Weighted Target Rate | — | None | Common |
| E5 Card, top row | — | — | Open Gaps | — | None | Common |
| E6 Card, top right | — | — | Variance pp | — | None; color by Target Status Color | Common |
| E7 Line chart, middle left, compliance versus target | DimDate[YearMonth] | Compliance Rate; Weighted Target Rate | Tooltips: Eligible Opportunities, MoM Change pp | —; two measure series provide series names | Eligible Opportunities > 0; YearMonth ascending; Y 0 to 1 | Common |
| E8 Clustered bar, middle right, provider performance | Compliance Rate; Weighted Target Rate | DimProvider[Provider_Group] | Tooltips: Eligible Opportunities, Open Gaps, Provider Rank | —; two measure series | Eligible Opportunities > 0; Compliance Rate descending; X 0 to 1 | Common |
| E9 Clustered bar, bottom left, regional open gaps | Open Gaps | DimRegion[Region] | Tooltips: Eligible Opportunities, Compliance Rate | — | Open Gaps > 0; Open Gaps descending | Common |
| E10 Table, bottom right, improvement priorities | — | — | Columns in order: DimMeasure[Measure_Name], Compliance Rate, Weighted Target Rate, Variance pp, Additional Closures To Target | — | Eligible Opportunities > 0; Additional Closures To Target descending; color Variance pp by Target Status Color | Common |

### Page 2 Quality Measure Performance

| ID and visual | X-axis | Y-axis | Values or additional wells | Legend | Visual filters and sort | Slicers |
| --- | --- | --- | --- | --- | --- | --- |
| M1 Card, top left | — | — | Measures Below Target | — | None | Common |
| M2 Card, top center | — | — | Additional Closures To Target | — | None | Common |
| M3 Card, top right | — | — | Compliant Opportunities | — | None | Common |
| M4 Clustered bar, middle left, actual versus target | Compliance Rate; Weighted Target Rate | DimMeasure[Measure_Name] | Standard performance tooltips | —; two measure series | Eligible Opportunities > 0; Compliance Rate ascending; X 0 to 1 | Common |
| M5 Matrix, middle right, provider by measure | — | — | Rows: DimProvider[Provider_Group]; Columns: DimMeasure[Measure_Name]; Values: Compliance Rate | — | Eligible Opportunities > 0; provider alphabetical; conditional background red <60%, amber 60% to <75%, blue >=75% (display bands only) | Common |
| M6 Line chart, bottom left, measure trend | DimDate[YearMonth] | Compliance Rate | Tooltips: Eligible Opportunities, MoM Change pp | DimMeasure[Measure_Name] | Eligible Opportunities > 0; YearMonth ascending; Y 0 to 1 | Common |
| M7 Table, bottom right, scorecard | — | — | DimMeasure[Measure_Name], Eligible Opportunities, Compliant Opportunities, Open Gaps, Compliance Rate, Weighted Target Rate, Variance pp, Target Status | — | Eligible Opportunities > 0; Variance pp ascending | Common |

The matrix bands are presentation choices, not official rating cut points. Overall/provider rates are not risk-adjusted; use the matrix to compare providers within each measure.

### Page 3 Care Gap and Outreach Analysis

| ID and visual | X-axis | Y-axis | Values or additional wells | Legend | Visual filters and sort | Slicers |
| --- | --- | --- | --- | --- | --- | --- |
| O1 Card, top left | — | — | Open Gaps | — | None | Common + channel |
| O2 Card, top row | — | — | Unattempted Open Gaps | — | None | Common + channel |
| O3 Card, top row | — | — | Attempted Gaps | — | None | Common + channel |
| O4 Card, top right | — | — | Outreach Closure Rate | — | None | Common + channel |
| O5 Stacked bar, middle left, open gaps by measure and region | Open Gaps | DimMeasure[Measure_Name] | Tooltips: Unattempted Open Gaps, Unreachable Open Gaps | DimRegion[Region] | Open Gaps > 0; Open Gaps descending | Common + channel |
| O6 Clustered column, middle right, channel closure and reach | FactQuality[Outreach_Channel] | Outreach Closure Rate; Reach Rate | Tooltips: Attempted Gaps, Closed Gaps, Average Attempts Per Gap | —; two measure series | Outreach_Channel is not None; Attempted Gaps > 0; Outreach Closure Rate descending; Y 0 to 1 | Common + channel |
| O7 Table, bottom left, outreach performance | — | — | FactQuality[Outreach_Channel], Attempted Gaps, Reached Gaps, Closed Gaps, Total Outreach Attempts, Outreach Closure Rate, Closure Among Reached | — | Outreach_Channel is not None; Attempted Gaps > 0; Outreach Closure Rate descending | Common + channel |
| O8 Table, bottom right, synthetic care-gap worklist | — | — | FactQuality[Member_ID], DimMeasure[Measure_Name], DimProvider[Provider_Group], DimRegion[Region], FactQuality[Measurement_Month], FactQuality[Outreach_Attempts], FactQuality[Outreach_Channel], FactQuality[Outreach_Status] | — | FactQuality[Eligible_Flag]=1 AND FactQuality[Compliant_Flag]=0; sort Outreach_Attempts ascending then Member_ID ascending; Don't summarize columns | Common + channel |

O8 uses dimension fields from the many-to-one lookups and fact detail fields; one row per unique member-measure. Outreach comparisons are descriptive associations in simulated data; no randomized study or cost effectiveness claim is made. Month is an assessment bucket, not elapsed follow-up time.

### Page 4 Data Quality Monitoring

| ID and visual | X-axis | Y-axis | Values or additional wells | Legend | Visual filters and sort | Slicers |
| --- | --- | --- | --- | --- | --- | --- |
| D1 Card, top left | — | — | DQ Staging Rows | — | None | Common |
| D2 Card, top row | — | — | DQ Affected Rows | — | None | Common |
| D3 Card, top row | — | — | DQ Valid Row Rate | — | None | Common |
| D4 Card, top right | — | — | DQ Duplicate Excess Rows | — | None | Common |
| D5 Clustered bar, middle left, violations by rule | DQ Rule Violations | DQRule[Rule_Name] | Tooltips: DQRule[Rule_ID] | — | Show items with no data on; DQ Rule Violations descending; include zero rules | Common |
| D6 Line chart, middle right, issue rate by month | DimDate[YearMonth] | DQ Issue Row Rate | Tooltips: DQ Staging Rows, DQ Affected Rows | — | DQ Staging Rows > 0; YearMonth ascending; Y 0 to 0.02 initially (auto-expand if needed) | Common |
| D7 Matrix, bottom left, source review by provider | — | — | Rows: DimProvider[Provider_Group]; Columns: DQAudit[DQ_Status]; Values: DQ Staging Rows | — | DQ Staging Rows > 0; provider alphabetical | Common |
| D8 Table, bottom right, failed checks | — | — | DQErrors[Row_ID], DQAudit[Member_ID], DimMeasure[Measure_Name], DimProvider[Provider_Group], DimRegion[Region], DQAudit[Measurement_Month], DQRule[Rule_ID], DQRule[Rule_Name] | — | No filter needed (DQErrors only contains failures); Row_ID ascending; all columns Don't summarize | Common; D5 selection additionally filters this table |

DQ rule counts and affected-row counts are different concepts. They happen to both be 66 in this version because seeded defects do not overlap. DQAudit Row_ID is the staging CSV data-row number (header excluded). It is not a patient identifier. Page 4 uses the staging audit, while pages 1-3 use only the clean dataset.

## 4. Acceptance checks in Power BI Desktop

With all slicers cleared, confirm: Total Records 8,000; Unique Members 3,075; Eligible Opportunities 5,884; Compliant Opportunities 4,173; Compliance Rate 70.9%; Open Gaps 1,711; Weighted Target Rate 79.5%; Variance pp -8.5; Additional Closures To Target 531; Measures Below Target 5.

Outreach: Starting Gaps 2,185; Attempted Gaps 1,640; Reached Gaps 1,025; Closed Gaps 474; Outreach Closure Rate 28.9%; Unattempted Open Gaps 545. DQ: 8,020 staging rows; 66 affected; 99.2% valid; 20 duplicate excess rows.

Select Colorectal Cancer Screening: 924 eligible, 531 compliant, 57.5% compliance, 393 open gaps, target 75.0%, additional closures 162. Select January 2026: 64.3% compliance and MoM Change pp blank. Select June 2026: 76.1%, MoM Change pp 1.0. Clear selections.

Select Provider Group C: 1,189 eligible and 61.2% compliance. Check all common slicers affect both clean metrics and staging audit. Select R02 on D5: error detail narrows to 20 duplicates, staging cards remain unchanged. Clear selections.

Select a combination with no eligible records: rates must be blank. Confirm totals divide summed numerators by summed denominators rather than averaging rates. Additional closures must total 531, not 503 (the rounded shortfall against the blended target), because excess medication performance cannot offset other measure deficits.

Save as `Medicare_Advantage_Quality_Improvement.pbix`. Export page screenshots or PDF, add the page 1 screenshot and project copy to your existing portfolio, then share the one-page summary and project link with the recruiter. Describe Power BI as implemented only after completing these Desktop checks.

## 5. Reference documentation

- [Microsoft CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax) for filter context.
- [Microsoft DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax) for blank rates when denominator is zero.
- [Microsoft date tables](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables).
- [CMS Part C and D Performance Data](https://www.cms.gov/medicare/health-drug-plans/part-c-d-performance-data) for official rating resources. This project does not reproduce those specifications or calculate Stars.
