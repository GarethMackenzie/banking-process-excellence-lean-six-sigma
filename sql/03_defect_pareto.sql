WITH defects AS (
  SELECT 'Documentation completeness' AS defect, SUM(Documentation_Completeness_Defect) AS n FROM applications_clean
  UNION ALL SELECT 'Document quality', SUM(Document_Quality_Defect) FROM applications_clean
  UNION ALL SELECT 'Identity verification', SUM(Identity_Verification_Defect) FROM applications_clean
  UNION ALL SELECT 'Data capture', SUM(Data_Capture_Defect) FROM applications_clean
  UNION ALL SELECT 'KYC processing', SUM(KYC_Processing_Defect) FROM applications_clean
  UNION ALL SELECT 'Product information', SUM(Product_Information_Defect) FROM applications_clean
), ranked AS (
  SELECT defect, n, SUM(n) OVER () AS total_n,
         SUM(n) OVER (ORDER BY n DESC ROWS UNBOUNDED PRECEDING) AS cumulative_n
  FROM defects
)
SELECT defect, n, 1.0*n/total_n AS share, 1.0*cumulative_n/total_n AS cumulative_share
FROM ranked ORDER BY n DESC;
