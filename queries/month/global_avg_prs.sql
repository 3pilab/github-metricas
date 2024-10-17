-- Promedio de PRs mensuales entre todos los desarrolladores
WITH user_prs_month AS (
    SELECT
        strftime('%Y-%m', created_at) AS month,
        COUNT(*) AS total_prs
    FROM
        pull_requests
    GROUP BY
        month
    ORDER BY
        month
)

SELECT AVG(total_prs) AS promedio_prs
FROM user_prs_month

