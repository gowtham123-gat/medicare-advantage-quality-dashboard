# Data dictionary and analytical definitions

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
