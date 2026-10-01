-- SQLite 3.25+ (window functions). Entirely synthetic demonstration data.
-- The raw table stays permissive so defects remain visible.
CREATE TABLE quality_fact (
 Member_ID TEXT NOT NULL, Age INTEGER NOT NULL, Gender TEXT NOT NULL,
 Region TEXT NOT NULL, Provider_Group TEXT NOT NULL, Measure_Name TEXT NOT NULL,
 Eligible_Flag INTEGER NOT NULL CHECK(Eligible_Flag IN (0,1)),
 Compliant_Flag INTEGER NOT NULL CHECK(Compliant_Flag IN (0,1) AND Compliant_Flag<=Eligible_Flag),
 Gap_Status TEXT NOT NULL, Measurement_Month TEXT NOT NULL,
 Outreach_Attempts INTEGER NOT NULL CHECK(Outreach_Attempts BETWEEN 0 AND 4),
 Outreach_Channel TEXT NOT NULL, Outreach_Status TEXT NOT NULL,
 Gap_Closed INTEGER NOT NULL CHECK(Gap_Closed IN (0,1)), Target_Rate REAL NOT NULL,
 PRIMARY KEY(Member_ID,Measure_Name)
);
CREATE TABLE quality_staging (
 Member_ID TEXT, Age INTEGER, Gender TEXT, Region TEXT, Provider_Group TEXT,
 Measure_Name TEXT, Eligible_Flag INTEGER, Compliant_Flag INTEGER,
 Gap_Status TEXT, Measurement_Month TEXT, Outreach_Attempts INTEGER,
 Outreach_Channel TEXT, Outreach_Status TEXT, Gap_Closed INTEGER, Target_Rate REAL
);
CREATE TABLE measure_targets (Measure_Name TEXT PRIMARY KEY, Target_Rate REAL NOT NULL);
CREATE INDEX idx_fact_month ON quality_fact(Measurement_Month);
CREATE INDEX idx_fact_provider ON quality_fact(Provider_Group,Measure_Name);
