# Analysis findings and recommendations

This project uses entirely synthetic data created for demonstration purposes. No PHI, PII, patient records, or proprietary employer data are included.

## Findings

1. Overall performance leaves a clear backlog. 4,173 of 5,884 eligible member-measure opportunities are compliant (70.9%), versus a 79.5% eligibility-weighted demonstration target. There are 1,711 open gaps. The aggregate difference is -8.5 percentage points.

2. Two measures account for most target shortfall. Colorectal Cancer Screening is 57.5% versus a 75.0% target, with 393 open gaps and 162 additional closures needed. Follow-Up After Hospitalization is 53.0% versus 75.0%, with 311 open gaps and 146 additional closures needed. Together they account for 308 of 531 required closures (58.0%). Medication Adherence is above its 85.0% target at 86.9%.

3. Provider Group C needs focused review. Its compliance is 61.2% (728/1,189), compared with 77.5% (1,131/1,459) for Group A, a 16.3 percentage-point difference. Group C has 461 open gaps, 26.9% of the total. These are unadjusted comparisons; check the provider-by-measure matrix before interpreting the overall rank.

4. The South region carries the largest backlog. It has 604 open gaps, 35.3% of all open gaps, and 66.5% compliance (1,200/1,804). The North has 74.4% compliance (1,143/1,536). The 7.9-point difference identifies a region for operational investigation, not a proven cause.

5. Monthly assessed cohorts show an improving trend. Compliance rises from 64.3% in January (657/1,021) to 76.1% in June (754/991), an 11.7-point difference. Each member-measure occurs once in the dataset, so these are different assessed cohorts, not repeated monthly snapshots or proof of a sustained longitudinal intervention effect.

6. Outreach has both promising channels and an uncovered backlog. Care Coordinator outreach closes 128/193 attempted gaps (66.3%), versus Phone 206/686 (30.0%), SMS 102/408 (25.0%), and Mail 38/353 (10.8%). Overall, 474/1,640 attempted gaps close (28.9%). 545 open gaps have no outreach attempt, 31.9% of the remaining backlog. Channel selection and synthetic generation can explain differences; no causal superiority is established.

7. Data-quality monitoring catches every seeded defect. The separate staging file has 8,020 rows and 66 affected rows (0.82%), including 20 duplicate excess rows, 8 missing member IDs, 8 out-of-cohort ages, 10 conflicting flags, 12 missing outreach channels, and 8 reference-target mismatches. Valid-row rate is 99.18%. The clean 8,000-row file passes the same ten rules with zero detected violations. The clean file is the original synthetic reference, not evidence of an automated staging repair process.

## Recommendations

1. Prioritize Colorectal Cancer Screening and Follow-Up After Hospitalization. Build measure-specific worklists and review unresolved gaps weekly. Use 162 and 146 additional closures as arithmetic planning targets with the current denominators held fixed; these are not forecasts or promised outcomes.

2. Review Provider Group C and the South region with operations staff. Compare the same measure and month, confirm gap evidence, and investigate scheduling or outreach barriers before assigning performance causes. Track open gaps, numerator, denominator, and variance to target.

3. Address the 545 unattempted open gaps. Start with gaps in the two highest-shortfall measures, assign an outreach owner, and track attempted, reached, and closed counts separately. A zero attempt must not be mistaken for an unsuccessful contact.

4. Pilot a channel escalation workflow. Keep SMS/phone for routine outreach and evaluate coordinator follow-up for selected unresolved gaps. Compare similar populations and capture cost and time before deciding whether the higher observed coordinator closure rate justifies broader use.

5. Run data-quality checks before every refresh. Quarantine unresolved errors, retain the staging source and audit row numbers, and reconcile clean counts with SQL and Power BI. Maintain reference targets separately and obtain approved specifications before any real operational use.

## Interpretation limits

Targets, eligibility and channel probabilities are demonstration assumptions. Diabetes Care is a broad synthetic indicator, Medication Adherence is not a drug-class-specific PDC calculation, and Follow-Up After Hospitalization is not a replicated official measure. There are no clinical event dates, claims, pharmacy fills, enrollment periods, exclusions or audited source records. This project does not calculate CMS Stars or certified HEDIS measures. No real savings, quality improvement, patient outcome or employer result is claimed. See data_dictionary.md for the exact definitions.
