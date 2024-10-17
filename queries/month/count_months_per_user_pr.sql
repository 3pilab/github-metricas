-- Query para obtener en cuantos meses aparece cada usuario
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

SELECT user, COUNT(*)
FROM user_prs_month
GROUP BY user

