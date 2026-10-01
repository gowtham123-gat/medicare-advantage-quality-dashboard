-- Run after import. SELECT * FROM each view to see results.
-- All rates are fractions (0-1); pp differences multiply by 100.
-- Denominator: eligible member-measure opportunities, not unique members.
CREATE VIEW v_overall AS
SELECT COUNT(*) AS Records, COUNT(DISTINCT Member_ID) AS Unique_Members,
 SUM(Eligible_Flag) AS Eligible_Opportunities,
 SUM(Compliant_Flag) AS Compliant_Opportunities,
 SUM(CASE WHEN Gap_Status='Open' THEN 1 ELSE 0 END) AS Open_Gaps,
 1.0*SUM(Compliant_Flag)/NULLIF(SUM(Eligible_Flag),0) AS Compliance_Rate,
 SUM(Eligible_Flag*Target_Rate)/NULLIF(SUM(Eligible_Flag),0) AS Weighted_Target_Rate,
 SUM(Gap_Closed) AS Closed_Gaps,
 SUM(CASE WHEN Eligible_Flag=1 AND (Compliant_Flag=0 OR Gap_Closed=1) THEN 1 ELSE 0 END) AS Starting_Gaps
FROM quality_fact;

CREATE VIEW v_measure_performance AS
SELECT Measure_Name, SUM(Eligible_Flag) AS Eligible_Opportunities,
 SUM(Compliant_Flag) AS Compliant_Opportunities,
 SUM(CASE WHEN Gap_Status='Open' THEN 1 ELSE 0 END) AS Open_Gaps,
 1.0*SUM(Compliant_Flag)/NULLIF(SUM(Eligible_Flag),0) AS Compliance_Rate,
 MAX(Target_Rate) AS Target_Rate,
 100*(1.0*SUM(Compliant_Flag)/NULLIF(SUM(Eligible_Flag),0)-MAX(Target_Rate)) AS Variance_pp
FROM quality_fact GROUP BY Measure_Name;

CREATE VIEW v_provider_performance AS
SELECT Provider_Group, SUM(Eligible_Flag) AS Eligible_Opportunities,
 SUM(Compliant_Flag) AS Compliant_Opportunities,
 SUM(CASE WHEN Gap_Status='Open' THEN 1 ELSE 0 END) AS Open_Gaps,
 1.0*SUM(Compliant_Flag)/NULLIF(SUM(Eligible_Flag),0) AS Compliance_Rate,
 SUM(Eligible_Flag*Target_Rate)/NULLIF(SUM(Eligible_Flag),0) AS Weighted_Target_Rate
FROM quality_fact GROUP BY Provider_Group;

CREATE VIEW v_region_performance AS
SELECT Region, SUM(Eligible_Flag) AS Eligible_Opportunities,
 SUM(Compliant_Flag) AS Compliant_Opportunities,
 SUM(CASE WHEN Gap_Status='Open' THEN 1 ELSE 0 END) AS Open_Gaps,
 1.0*SUM(Compliant_Flag)/NULLIF(SUM(Eligible_Flag),0) AS Compliance_Rate
FROM quality_fact GROUP BY Region;

CREATE VIEW v_care_gaps AS
SELECT Measure_Name, Provider_Group, Region,
 COUNT(*) AS Open_Gaps,
 COUNT(DISTINCT Member_ID) AS Members_With_Open_Gaps,
 SUM(CASE WHEN Outreach_Attempts=0 THEN 1 ELSE 0 END) AS Unattempted_Open_Gaps,
 SUM(CASE WHEN Outreach_Status='Unable to Reach' THEN 1 ELSE 0 END) AS Unreachable_Open_Gaps
FROM quality_fact WHERE Eligible_Flag=1 AND Compliant_Flag=0
GROUP BY Measure_Name,Provider_Group,Region;

CREATE VIEW v_monthly_trend AS
WITH monthly AS (
 SELECT Measurement_Month, SUM(Eligible_Flag) AS Eligible_Opportunities,
 SUM(Compliant_Flag) AS Compliant_Opportunities,
 SUM(CASE WHEN Gap_Status='Open' THEN 1 ELSE 0 END) AS Open_Gaps,
 1.0*SUM(Compliant_Flag)/NULLIF(SUM(Eligible_Flag),0) AS Compliance_Rate,
 SUM(Eligible_Flag*Target_Rate)/NULLIF(SUM(Eligible_Flag),0) AS Weighted_Target_Rate
 FROM quality_fact GROUP BY Measurement_Month
)
SELECT *,100*(Compliance_Rate-LAG(Compliance_Rate) OVER (ORDER BY Measurement_Month)) AS MoM_Change_pp
FROM monthly ORDER BY Measurement_Month;

-- Includes attempted gaps only, so pre-existing compliant records are excluded.
-- Gap closures are observed in the same assessment month. Association is not causation.
CREATE VIEW v_outreach_effectiveness AS
SELECT Outreach_Channel, COUNT(*) AS Attempted_Gaps,
 SUM(CASE WHEN Outreach_Status='Reached' THEN 1 ELSE 0 END) AS Reached_Gaps,
 SUM(Gap_Closed) AS Closed_Gaps, SUM(Outreach_Attempts) AS Total_Attempts,
 1.0*SUM(Gap_Closed)/NULLIF(COUNT(*),0) AS Closure_Rate,
 1.0*SUM(CASE WHEN Outreach_Status='Reached' THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0) AS Reach_Rate,
 1.0*SUM(Gap_Closed)/NULLIF(SUM(CASE WHEN Outreach_Status='Reached' THEN 1 ELSE 0 END),0) AS Closure_Among_Reached,
 1.0*SUM(Outreach_Attempts)/NULLIF(COUNT(*),0) AS Average_Attempts
FROM quality_fact WHERE Eligible_Flag=1 AND Outreach_Attempts>0
GROUP BY Outreach_Channel;

CREATE VIEW v_target_opportunity AS
WITH calc AS (
 SELECT *,Eligible_Opportunities*Target_Rate AS Required_Unrounded
 FROM v_measure_performance
)
SELECT Measure_Name, Eligible_Opportunities, Compliant_Opportunities,
 Compliance_Rate, Target_Rate, Variance_pp,
 MAX(0, CAST(Required_Unrounded AS INTEGER)+
 CASE WHEN Required_Unrounded>CAST(Required_Unrounded AS INTEGER) THEN 1 ELSE 0 END
 -Compliant_Opportunities) AS Additional_Closures_To_Target
FROM calc ORDER BY Additional_Closures_To_Target DESC;

-- Supplemental: compare providers within the same measure before interpreting ranks.
CREATE VIEW v_provider_measure AS
SELECT Provider_Group,Measure_Name,SUM(Eligible_Flag) AS Eligible_Opportunities,
 SUM(Compliant_Flag) AS Compliant_Opportunities,
 1.0*SUM(Compliant_Flag)/NULLIF(SUM(Eligible_Flag),0) AS Compliance_Rate,
 100*(1.0*SUM(Compliant_Flag)/NULLIF(SUM(Eligible_Flag),0)-MAX(Target_Rate)) AS Variance_pp
FROM quality_fact GROUP BY Provider_Group,Measure_Name;
