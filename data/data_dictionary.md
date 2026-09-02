# Data Dictionary

Canonical synthetic application dataset. Fields are synthetic and contain no real customer data.

| Field | Type | Description |
|---|---|---|
| `Application_Date` | object | Synthetic application date. |
| `Application_ID` | object | Synthetic application id. |
| `Application_Month` | object | Synthetic application month. |
| `Channel` | object | Synthetic channel. |
| `Customer_Segment` | object | Synthetic customer segment. |
| `Product_Type` | object | Synthetic product type. |
| `Region` | object | Synthetic region. |
| `Branch_ID` | object | Synthetic branch id. |
| `Shift` | object | Synthetic shift. |
| `Application_Received_Timestamp` | object | Synthetic application received timestamp. |
| `Product_Risk_Class` | int64 | Synthetic product risk class. |
| `Ownership_Complexity_Flag` | int64 | Synthetic ownership complexity flag. |
| `Identity_Exception_History_Flag` | int64 | Synthetic identity exception history flag. |
| `Source_Channel_Risk` | int64 | Synthetic source channel risk. |
| `Enhanced_Due_Diligence_Flag` | int64 | Synthetic enhanced due diligence flag. |
| `Verification_Risk_Score` | float64 | Synthetic verification risk score. |
| `Risk_Score` | float64 | Synthetic risk score. |
| `Risk_Tier` | object | Synthetic risk tier. |
| `Products_Requested` | int64 | Synthetic products requested. |
| `Documents_Required` | int64 | Synthetic documents required. |
| `Complexity_Score` | int64 | Synthetic complexity score. |
| `Application_Complexity` | object | Synthetic application complexity. |
| `Opening_Backlog` | float64 | Synthetic opening backlog. |
| `Closing_Backlog` | float64 | Synthetic closing backlog. |
| `Effective_Capacity` | float64 | Synthetic effective capacity. |
| `Available_Staff` | float64 | Synthetic available staff. |
| `Senior_Reviewer_Count` | float64 | Synthetic senior reviewer count. |
| `KYC_Specialist_Count` | float64 | Synthetic kyc specialist count. |
| `System_Downtime_Minutes` | float64 | Synthetic system downtime minutes. |
| `Arrival_Rank_In_Shift` | int64 | Synthetic arrival rank in shift. |
| `Queue_Length_At_Arrival` | int64 | Synthetic queue length at arrival. |
| `Queue_Position_At_Arrival` | int64 | Synthetic queue position at arrival. |
| `Documentation_Completeness_Defect` | int64 | Synthetic documentation completeness defect. |
| `Document_Quality_Defect` | int64 | Synthetic document quality defect. |
| `Identity_Verification_Defect` | int64 | Synthetic identity verification defect. |
| `Data_Capture_Defect` | int64 | Synthetic data capture defect. |
| `KYC_Processing_Defect` | int64 | Synthetic kyc processing defect. |
| `Product_Information_Defect` | int64 | Synthetic product information defect. |
| `Defect_Count` | int64 | Synthetic defect count. |
| `Missing_Document_Flag` | int64 | Synthetic missing document flag. |
| `Document_Error_Flag` | int64 | Synthetic document error flag. |
| `Identity_Mismatch_Flag` | int64 | Synthetic identity mismatch flag. |
| `Documents_Submitted` | int64 | Synthetic documents submitted. |
| `Rework_Count` | int64 | Synthetic rework count. |
| `Rework_Flag` | int64 | Synthetic rework flag. |
| `Rework_Minutes` | float64 | Synthetic rework minutes. |
| `Required_Manual_Review_Flag` | int64 | Synthetic required manual review flag. |
| `Defect_Driven_Review_Flag` | int64 | Synthetic defect driven review flag. |
| `Manual_Review_Flag` | int64 | Synthetic manual review flag. |
| `Exception_Flag` | int64 | Synthetic exception flag. |
| `Analyst_ID` | object | Synthetic analyst id. |
| `Analyst_Workload_At_Assignment` | int64 | Synthetic analyst workload at assignment. |
| `Queue_Time_Minutes` | float64 | Synthetic queue time minutes. |
| `Identity_Verification_Minutes` | float64 | Synthetic identity verification minutes. |
| `Document_Validation_Minutes` | float64 | Synthetic document validation minutes. |
| `KYC_Batch_Wait_Minutes` | float64 | Synthetic kyc batch wait minutes. |
| `KYC_Processing_Minutes` | float64 | Synthetic kyc processing minutes. |
| `Manual_Review_Queue_Wait_Minutes` | float64 | Synthetic manual review queue wait minutes. |
| `Manual_Review_Minutes` | float64 | Synthetic manual review minutes. |
| `Abandonment_Flag` | int64 | Synthetic abandonment flag. |
| `Application_Abandoned_Flag` | int64 | Synthetic application abandoned flag. |
| `Completed_Flag` | int64 | Synthetic completed flag. |
| `Application_Status` | object | Synthetic application status. |
| `Abandonment_Stage` | object | Synthetic abandonment stage. |
| `Identity_Verification_Start` | object | Synthetic identity verification start. |
| `Identity_Verification_End` | object | Synthetic identity verification end. |
| `Document_Validation_Start` | object | Synthetic document validation start. |
| `Document_Validation_End` | object | Synthetic document validation end. |
| `KYC_Start` | object | Synthetic kyc start. |
| `KYC_End` | object | Synthetic kyc end. |
| `Manual_Review_Start` | object | Synthetic manual review start. |
| `Manual_Review_End` | object | Synthetic manual review end. |
| `Abandonment_Timestamp` | object | Synthetic abandonment timestamp. |
| `Approval_Timestamp` | object | Synthetic approval timestamp. |
| `Activation_Timestamp` | object | Synthetic activation timestamp. |
| `Time_To_Approval_Hours` | float64 | Synthetic time to approval hours. |
| `Time_To_Activation_Hours` | float64 | Synthetic time to activation hours. |
| `Elapsed_Time_To_Abandonment_Hours` | float64 | Synthetic elapsed time to abandonment hours. |
| `Elapsed_Process_Hours` | float64 | Synthetic elapsed process hours. |
| `Total_Onboarding_Hours` | float64 | Synthetic total onboarding hours. |
| `SLA_Target_Hours` | float64 | Synthetic sla target hours. |
| `SLA_Utilization` | float64 | Synthetic sla utilization. |
| `SLA_Margin_Hours` | float64 | Synthetic sla margin hours. |
| `SLA_Met_Flag` | float64 | Synthetic sla met flag. |
| `First_Pass_Yield_Flag` | int64 | Synthetic first pass yield flag. |
| `Customer_Complaint_Flag` | int64 | Synthetic customer complaint flag. |
| `Prevention_Cost` | float64 | Synthetic prevention cost. |
| `Required_Manual_Review_Cost` | float64 | Synthetic required manual review cost. |
| `Defect_Driven_Review_Cost` | float64 | Synthetic defect driven review cost. |
| `Rework_Cost` | float64 | Synthetic rework cost. |
| `Repeat_Processing_Cost` | float64 | Synthetic repeat processing cost. |
| `Complaint_Cost` | float64 | Synthetic complaint cost. |
| `Abandonment_Cost` | float64 | Synthetic abandonment cost. |
| `Expedited_Handling_Cost` | float64 | Synthetic expedited handling cost. |
| `Total_Prevention_Cost` | float64 | Synthetic total prevention cost. |
| `Total_Appraisal_Cost` | float64 | Synthetic total appraisal cost. |
| `Total_Internal_Failure_Cost` | float64 | Synthetic total internal failure cost. |
| `Total_External_Failure_Cost` | float64 | Synthetic total external failure cost. |
| `Total_COPQ` | float64 | Synthetic total copq. |
| `Total_Cost_of_Quality` | float64 | Synthetic total cost of quality. |
| `COPQ_Rework_Cost` | float64 | Synthetic copq rework cost. |
| `COPQ_Manual_Review_Cost` | float64 | Synthetic copq manual review cost. |
| `COPQ_Complaint_Cost` | float64 | Synthetic copq complaint cost. |
| `COPQ_Abandonment_Cost` | float64 | Synthetic copq abandonment cost. |