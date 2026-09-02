WITH completed AS (
  SELECT Application_ID, Channel, Application_Complexity, Time_To_Activation_Hours,
         ROW_NUMBER() OVER (PARTITION BY Channel ORDER BY Time_To_Activation_Hours) AS rn,
         COUNT(*) OVER (PARTITION BY Channel) AS n
  FROM applications_clean
  WHERE Completed_Flag = 1
)
SELECT Channel, Application_Complexity, AVG(Time_To_Activation_Hours) AS avg_cycle_hours
FROM completed
GROUP BY Channel, Application_Complexity;
