copy(
WITH 

std_stay AS (
    SELECT *
    FROM churn_results
    WHERE subscription_type = 'Standard'
      AND prediction = 'WILL STAY'
    ORDER BY random()
    LIMIT 42737
),
std_leave AS (
    SELECT *
    FROM churn_results
    WHERE subscription_type = 'Standard'
      AND prediction = 'WILL LEAVE'
    ORDER BY random()
    LIMIT 10487
),


basic_stay AS (
    SELECT *
    FROM churn_results
    WHERE subscription_type = 'Basic'
      AND prediction = 'WILL STAY'
    ORDER BY random()
    LIMIT 33660
),
basic_leave AS (
    SELECT *
    FROM churn_results
    WHERE subscription_type = 'Basic'
      AND prediction = 'WILL LEAVE'
    ORDER BY random()
    LIMIT 4768
),


prem_stay AS (
    SELECT *
    FROM churn_results
    WHERE subscription_type = 'Premium'
      AND prediction = 'WILL STAY'
    ORDER BY random()
    LIMIT 8975
),
prem_leave AS (
    SELECT *
    FROM churn_results
    WHERE subscription_type = 'Premium'
      AND prediction = 'WILL LEAVE'
    ORDER BY random()
    LIMIT 482
)


SELECT * FROM std_stay
UNION ALL
SELECT * FROM std_leave
UNION ALL
SELECT * FROM basic_stay
UNION ALL
SELECT * FROM basic_leave
UNION ALL
SELECT * FROM prem_stay
UNION ALL
SELECT * FROM prem_leave
)TO 'C:/Users/amet1/Downloads/.Courses/DEPI/final project/PT/new.csv'
WITH (FORMAT CSV, HEADER, ENCODING 'UTF8');