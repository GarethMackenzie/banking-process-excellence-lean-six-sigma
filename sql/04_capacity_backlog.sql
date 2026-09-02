SELECT Date, Branch_ID, Shift, Opening_Backlog, New_Arrivals, Effective_Capacity,
       Processed_Count, Closing_Backlog,
       LAG(Closing_Backlog) OVER (PARTITION BY Branch_ID, Shift ORDER BY Date) AS prior_closing_backlog
FROM capacity_schedule;
