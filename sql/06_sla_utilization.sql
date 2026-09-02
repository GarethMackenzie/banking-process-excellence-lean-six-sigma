SELECT Application_Complexity, SLA_Target_Hours,
       COUNT(*) AS completed_applications,
       AVG(SLA_Utilization) AS avg_sla_utilization,
       AVG(SLA_Met_Flag) AS sla_compliance
FROM applications_clean
WHERE Completed_Flag = 1
GROUP BY Application_Complexity, SLA_Target_Hours;
