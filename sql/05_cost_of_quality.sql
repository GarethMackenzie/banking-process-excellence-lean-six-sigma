SELECT
  SUM(Total_Prevention_Cost) AS prevention_cost,
  SUM(Total_Appraisal_Cost) AS appraisal_cost,
  SUM(Total_Internal_Failure_Cost) AS internal_failure_cost,
  SUM(Total_External_Failure_Cost) AS external_failure_cost,
  SUM(Total_COPQ) AS copq,
  SUM(Total_Cost_of_Quality) AS total_cost_of_quality
FROM applications_clean;
