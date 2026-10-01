-- Evaluate staging BEFORE imposing clean-table constraints.
-- Duplicate rule flags later occurrences only, allowing one retained record.
CREATE VIEW dq_evaluated AS
SELECT s.rowid AS Row_ID,s.*,
 ROW_NUMBER() OVER(PARTITION BY Member_ID,Measure_Name ORDER BY s.rowid) AS Key_Occurrence,
 t.Target_Rate AS Expected_Target
FROM quality_staging s LEFT JOIN measure_targets t USING(Measure_Name);

CREATE VIEW dq_errors AS
SELECT Row_ID,'R01' AS Rule_ID,'Missing member or measure key' AS Rule_Name FROM dq_evaluated
 WHERE TRIM(COALESCE(Member_ID,''))='' OR TRIM(COALESCE(Measure_Name,''))=''
UNION ALL SELECT Row_ID,'R02','Duplicate member-measure key' FROM dq_evaluated
 WHERE Key_Occurrence>1 AND TRIM(COALESCE(Member_ID,''))<>'' AND TRIM(COALESCE(Measure_Name,''))<>''
UNION ALL SELECT Row_ID,'R03','Age outside demo cohort' FROM dq_evaluated
 WHERE Age IS NULL OR Age NOT BETWEEN 65 AND 89
UNION ALL SELECT Row_ID,'R04','Invalid or conflicting flags' FROM dq_evaluated
 WHERE Eligible_Flag IS NULL OR Compliant_Flag IS NULL OR Gap_Closed IS NULL
 OR Eligible_Flag NOT IN(0,1) OR Compliant_Flag NOT IN(0,1) OR Gap_Closed NOT IN(0,1)
 OR Compliant_Flag>Eligible_Flag
UNION ALL SELECT Row_ID,'R05','Gap status or closure conflict' FROM dq_evaluated
 WHERE Gap_Status IS NULL OR Gap_Status<>CASE WHEN Eligible_Flag=0 THEN 'Not Eligible' WHEN Compliant_Flag=1 THEN 'Compliant' ELSE 'Open' END
 OR (Gap_Closed=1 AND (Eligible_Flag<>1 OR Compliant_Flag<>1 OR Outreach_Attempts<=0 OR Outreach_Status<>'Reached'))
UNION ALL SELECT Row_ID,'R06','Outreach field inconsistency' FROM dq_evaluated
 WHERE Outreach_Attempts IS NULL OR Outreach_Attempts NOT BETWEEN 0 AND 4
 OR Outreach_Channel IS NULL OR Outreach_Status IS NULL
 OR (Outreach_Attempts>0 AND (Outreach_Channel NOT IN('Phone','SMS','Mail','Care Coordinator') OR Outreach_Status NOT IN('Reached','Unable to Reach','Declined')))
 OR (Outreach_Attempts=0 AND (Outreach_Channel<>'None' OR Outreach_Status NOT IN('Not Needed','Not Attempted')))
 OR (Outreach_Attempts>0 AND (Eligible_Flag<>1 OR (Compliant_Flag=1 AND Gap_Closed=0)))
 OR (Outreach_Attempts=0 AND Outreach_Status<>CASE WHEN Eligible_Flag=1 AND Compliant_Flag=0 THEN 'Not Attempted' ELSE 'Not Needed' END)
UNION ALL SELECT Row_ID,'R07','Target differs from demo reference' FROM dq_evaluated
 WHERE Target_Rate IS NULL OR Expected_Target IS NULL OR ABS(Target_Rate-Expected_Target)>0.000001
UNION ALL SELECT Row_ID,'R08','Invalid measurement month' FROM dq_evaluated
 WHERE Measurement_Month IS NULL OR Measurement_Month NOT IN('2026-01-01','2026-02-01','2026-03-01','2026-04-01','2026-05-01','2026-06-01')
UNION ALL SELECT Row_ID,'R09','Missing or unknown dimension' FROM dq_evaluated
 WHERE Gender IS NULL OR Gender NOT IN('Female','Male') OR Region IS NULL OR Region NOT IN('North','South','East','West')
 OR Provider_Group IS NULL OR Provider_Group NOT IN('Provider Group A','Provider Group B','Provider Group C','Provider Group D','Provider Group E')
UNION ALL SELECT Row_ID,'R10','Eligibility outside demo age gender rule' FROM dq_evaluated
 WHERE Eligible_Flag=1 AND Age BETWEEN 65 AND 89 AND
 ((Measure_Name='Colorectal Cancer Screening' AND Age>75) OR (Measure_Name='Breast Cancer Screening' AND (Age>74 OR Gender<>'Female')));

CREATE VIEW dq_audit AS
SELECT e.Row_ID,e.Member_ID,e.Region,e.Provider_Group,e.Measure_Name,e.Measurement_Month,
 COUNT(d.Rule_ID) AS Issue_Count,CASE WHEN COUNT(d.Rule_ID)=0 THEN 'Valid' ELSE 'Needs Review' END AS DQ_Status
FROM dq_evaluated e LEFT JOIN dq_errors d USING(Row_ID)
GROUP BY e.Row_ID,e.Member_ID,e.Region,e.Provider_Group,e.Measure_Name,e.Measurement_Month;

-- Audit summary. A row can fail several rules. Do not equate violations with rows.
SELECT COUNT(*) AS Staging_Rows,
 SUM(CASE WHEN Issue_Count>0 THEN 1 ELSE 0 END) AS Affected_Rows,
 SUM(Issue_Count) AS Rule_Violations,
 1.0*SUM(CASE WHEN Issue_Count=0 THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0) AS Valid_Row_Rate
FROM dq_audit;
SELECT Rule_ID,Rule_Name,COUNT(*) AS Rule_Violations FROM dq_errors GROUP BY Rule_ID,Rule_Name;
