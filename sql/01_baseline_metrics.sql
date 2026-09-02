-- ANSI-oriented baseline process metrics over the clean synthetic application fact.
SELECT
    COUNT(*) AS applications,
    AVG(CASE WHEN Completed_Flag = 1 THEN Time_To_Activation_Hours END) AS avg_activation_hours,
    AVG(CASE WHEN Completed_Flag = 1 THEN SLA_Met_Flag END) AS sla_compliance,
    AVG(First_Pass_Yield_Flag) AS first_pass_yield,
    AVG(Rework_Flag) AS rework_rate,
    AVG(Total_COPQ) AS copq_per_application
FROM applications_clean;
