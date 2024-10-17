
SELECT 
    strftime('%Y-%m', created_at) AS month,
    COUNT(*) AS total_prs           
FROM 
    pull_requests
GROUP BY 
    month
ORDER BY 
    month;
