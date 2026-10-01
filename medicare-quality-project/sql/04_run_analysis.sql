-- Query the supplied database; no schema recreation required.
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
