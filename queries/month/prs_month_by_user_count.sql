-- Query para obtener el total de PRs por mes y usuario
SELECT 
    user,
    strftime('%Y-%m', created_at) AS month,
    COUNT(*) AS total_prs
FROM
    pull_requests
GROUP BY 
    month, user
ORDER BY 
    month;
