-- Promedio de PRs mensuales por usuario
WITH user_prs_month AS (
    SELECT 
        user,
        strftime('%Y-%m', created_at) AS month,
        COUNT(*) AS total_prs
    FROM
        pull_requests
    GROUP BY 
        month, user
    ORDER BY 
        month
)

SELECT user, AVG(total_prs)
FROM user_prs_month
GROUP by user
ORDER by user
