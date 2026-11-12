-- How many unique customers are present in the dataset?

SELECT
    COUNT(DISTINCT customer_id) AS total_unique_customers
FROM customer_snapshots;

-- How many customer records and snapshots are available?

SELECT
    COUNT(*) AS total_customer_records,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT snapshot_date) AS total_snapshots
FROM customer_snapshots;

-- What is the overall churn rate?

SELECT
    COUNT(*) AS total_records,
    SUM(churn) AS churned_records,
    ROUND(
        100.0 * SUM(churn) / COUNT(*),
        2
    ) AS churn_rate_percentage
FROM customer_snapshots;

-- How many customers are churned versus non-churned?

SELECT
    CASE
        WHEN churn = 1 THEN 'Churned'
        ELSE 'Not Churned'
    END AS churn_status,
    COUNT(*) AS customer_records,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM customer_snapshots
GROUP BY churn
ORDER BY churn DESC;

-- How does the churn rate change across snapshots?

SELECT
    snapshot_date,
    COUNT(*) AS total_customers,
    SUM(churn) AS churned_customers,
    ROUND(
        100.0 * SUM(churn) / COUNT(*),
        2
    ) AS churn_rate_percentage
FROM customer_snapshots
GROUP BY snapshot_date
ORDER BY snapshot_date;

-- What is the churn rate across different age groups?

SELECT
    CASE
        WHEN age < 25 THEN 'Below 25'
        WHEN age BETWEEN 25 AND 34 THEN '25-34'
        WHEN age BETWEEN 35 AND 44 THEN '35-44'
        WHEN age BETWEEN 45 AND 54 THEN '45-54'
        WHEN age BETWEEN 55 AND 64 THEN '55-64'
        ELSE '65+'
    END AS age_group,
    COUNT(*) AS total_customers,
    SUM(churn) AS churned_customers,
    ROUND(
        100.0 * SUM(churn) / COUNT(*),
        2
    ) AS churn_rate
FROM latest_customers
WHERE age IS NOT NULL
GROUP BY age_group
ORDER BY churn_rate DESC;

-- Which locations have the highest churn rates?

SELECT
    location,
    COUNT(*) AS total_customers,
    SUM(churn) AS churned_customers,
    ROUND(
        100.0 * SUM(churn) / COUNT(*),
        2
    ) AS churn_rate
FROM latest_customers
WHERE location IS NOT NULL
GROUP BY location
HAVING COUNT(*) >= 50
ORDER BY churn_rate DESC;

-- How does occupation influence customer churn?

SELECT
    occupation,
    COUNT(*) AS total_customers,
    SUM(churn) AS churned_customers,
    ROUND(
        100.0 * SUM(churn) / COUNT(*),
        2
    ) AS churn_rate
FROM latest_customers
WHERE occupation IS NOT NULL
GROUP BY occupation
ORDER BY churn_rate DESC;

-- Which income brackets have the highest churn?

SELECT
    income_bracket,
    COUNT(*) AS total_customers,
    SUM(churn) AS churned_customers,
    ROUND(
        100.0 * SUM(churn) / COUNT(*),
        2
    ) AS churn_rate
FROM latest_customers
WHERE income_bracket IS NOT NULL
GROUP BY income_bracket
ORDER BY churn_rate DESC;

-- Which acquisition channels bring customers with the highest churn rates?

SELECT
    acquisition_channel,
    COUNT(*) AS total_customers,
    SUM(churn) AS churned_customers,
    ROUND(
        100.0 * SUM(churn) / COUNT(*),
        2
    ) AS churn_rate
FROM latest_customers
WHERE acquisition_channel IS NOT NULL
GROUP BY acquisition_channel
ORDER BY churn_rate DESC;

-- What is the total transaction volume and total transaction value?

SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(amount) AS total_transaction_value,
    ROUND(AVG(amount), 2) AS average_transaction_amount
FROM transactions;

-- What is the average transaction amount for each transaction type?

SELECT
    type,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_transaction_value,
    ROUND(AVG(amount), 2) AS average_transaction_amount
FROM transactions
GROUP BY type
ORDER BY average_transaction_amount DESC;

-- Which customers have the highest transaction frequency?

SELECT
    customer_id,
    COUNT(*) AS total_transactions,
    ROUND(AVG(amount), 2) AS average_transaction_amount
FROM transactions
GROUP BY customer_id
ORDER BY total_transactions DESC
LIMIT 10;

-- Which customers have the highest total transaction value?

SELECT
    customer_id,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_transaction_value,
    ROUND(AVG(amount), 2) AS average_transaction_amount
FROM transactions
GROUP BY customer_id
ORDER BY total_transaction_value DESC
LIMIT 10;

-- How does transaction activity change month by month?

SELECT
    DATE_TRUNC('month', date)::DATE AS transaction_month,
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT customer_id) AS active_customers,
    SUM(amount) AS total_transaction_value,
    ROUND(AVG(amount), 2) AS average_transaction_amount
FROM transactions
GROUP BY DATE_TRUNC('month', date)
ORDER BY transaction_month;

-- Which churned customers had transaction history in the last 90 days?

WITH transaction_summary AS (
    SELECT
        t.customer_id,
        COUNT(*) AS transaction_count,
        SUM(t.amount) AS total_transaction_value
    FROM transactions t
    CROSS JOIN (
        SELECT MAX(snapshot_date) AS latest_date
        FROM customer_snapshots
    ) d
    WHERE t.date > d.latest_date - INTERVAL '90 days'
      AND t.date <= d.latest_date
    GROUP BY t.customer_id
)
SELECT
    c.customer_id,
    c.churn,
    ts.transaction_count,
    ts.total_transaction_value
FROM latest_customers c
INNER JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
WHERE c.churn = 1
ORDER BY ts.total_transaction_value DESC
LIMIT 20;

-- Which customers had no transactions in the last 90 days?

WITH transaction_summary AS (
    SELECT
        t.customer_id,
        COUNT(*) AS transaction_count
    FROM transactions t
    CROSS JOIN (
        SELECT MAX(snapshot_date) AS latest_date
        FROM customer_snapshots
    ) d
    WHERE t.date > d.latest_date - INTERVAL '90 days'
      AND t.date <= d.latest_date
    GROUP BY t.customer_id
)
SELECT
    c.customer_id,
    c.churn,
    COALESCE(ts.transaction_count, 0) AS transaction_count
FROM latest_customers c
LEFT JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
WHERE ts.customer_id IS NULL
ORDER BY c.churn DESC;

-- Who are the highest-value churned customers?

WITH transaction_summary AS (
    SELECT
        t.customer_id,
        COUNT(*) AS transaction_count,
        SUM(t.amount) AS total_transaction_value
    FROM transactions t
    CROSS JOIN (
        SELECT MAX(snapshot_date) AS latest_date
        FROM customer_snapshots
    ) d
    WHERE t.date > d.latest_date - INTERVAL '90 days'
      AND t.date <= d.latest_date
    GROUP BY t.customer_id
)
SELECT
    c.customer_id,
    c.location,
    c.income_bracket,
    ts.transaction_count,
    ts.total_transaction_value
FROM latest_customers c
INNER JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
WHERE c.churn = 1
ORDER BY ts.total_transaction_value DESC
LIMIT 20;

-- What is the transaction value across different income brackets and churn statuses?

WITH transaction_summary AS (
    SELECT
        t.customer_id,
        COUNT(*) AS transaction_count,
        SUM(t.amount) AS total_transaction_value
    FROM transactions t
    CROSS JOIN (
        SELECT MAX(snapshot_date) AS latest_date
        FROM customer_snapshots
    ) d
    WHERE t.date > d.latest_date - INTERVAL '90 days'
      AND t.date <= d.latest_date
    GROUP BY t.customer_id
)
SELECT
    c.income_bracket,
    CASE
        WHEN c.churn = 1 THEN 'Churned'
        ELSE 'Not Churned'
    END AS churn_status,
    COUNT(*) AS customer_count,
    SUM(COALESCE(ts.transaction_count, 0)) AS total_transactions,
    SUM(COALESCE(ts.total_transaction_value, 0)) AS total_transaction_value
FROM latest_customers c
LEFT JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
GROUP BY
    c.income_bracket,
    c.churn
ORDER BY
    c.income_bracket,
    c.churn;

-- Which locations have the highest transaction exposure among churned customers?

WITH transaction_summary AS (
    SELECT
        t.customer_id,
        SUM(t.amount) AS total_transaction_value
    FROM transactions t
    CROSS JOIN (
        SELECT MAX(snapshot_date) AS latest_date
        FROM customer_snapshots
    ) d
    WHERE t.date > d.latest_date - INTERVAL '90 days'
      AND t.date <= d.latest_date
    GROUP BY t.customer_id
)
SELECT
    c.location,
    COUNT(*) AS churned_customers,
    SUM(COALESCE(ts.total_transaction_value, 0)) AS total_transaction_value
FROM latest_customers c
LEFT JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
WHERE c.churn = 1
GROUP BY c.location
ORDER BY total_transaction_value DESC;

-- How does transaction behaviour differ between churned and non-churned customers?

WITH transaction_summary AS (
    SELECT
        t.customer_id,
        COUNT(*) AS transaction_count,
        SUM(t.amount) AS total_transaction_value,
        AVG(t.amount) AS average_transaction_amount
    FROM transactions t
    CROSS JOIN (
        SELECT MAX(snapshot_date) AS latest_date
        FROM customer_snapshots
    ) d
    WHERE t.date > d.latest_date - INTERVAL '90 days'
      AND t.date <= d.latest_date
    GROUP BY t.customer_id
)
SELECT
    CASE
        WHEN c.churn = 1 THEN 'Churned'
        ELSE 'Not Churned'
    END AS churn_status,
    COUNT(*) AS customer_count,
    ROUND(AVG(COALESCE(ts.transaction_count, 0)), 2)
        AS avg_transaction_count,
    ROUND(AVG(COALESCE(ts.total_transaction_value, 0)), 2)
        AS avg_transaction_value,
    ROUND(AVG(ts.average_transaction_amount), 2)
        AS avg_transaction_size
FROM latest_customers c
LEFT JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
GROUP BY c.churn
ORDER BY c.churn DESC;

-- How many customers fall into each churn and transaction-value segment?

WITH transaction_summary AS (
    SELECT
        customer_id,
        SUM(amount) AS total_transaction_value
    FROM transactions
    WHERE date > (
        SELECT MAX(snapshot_date) - INTERVAL '90 days'
        FROM customer_snapshots
    )
    AND date <= (
        SELECT MAX(snapshot_date)
        FROM customer_snapshots
    )
    GROUP BY customer_id
),
customer_segments AS (
    SELECT
        c.customer_id,
        c.churn,
        COALESCE(ts.total_transaction_value, 0) AS transaction_value,
        CASE
            WHEN COALESCE(ts.total_transaction_value, 0) = 0
                THEN 'No Transaction'
            WHEN ts.total_transaction_value < 10000000
                THEN 'Low Value'
            WHEN ts.total_transaction_value < 50000000
                THEN 'Medium Value'
            ELSE 'High Value'
        END AS value_segment
    FROM latest_customers c
    LEFT JOIN transaction_summary ts
        ON c.customer_id = ts.customer_id
)
SELECT
    value_segment,
    CASE
        WHEN churn = 1 THEN 'Churned'
        ELSE 'Not Churned'
    END AS churn_status,
    COUNT(*) AS customer_count
FROM customer_segments
GROUP BY value_segment, churn
ORDER BY value_segment, churn DESC;

-- Who are the top 20 churned customers by transaction value?

WITH transaction_summary AS (
    SELECT
        customer_id,
        SUM(amount) AS total_transaction_value,
        COUNT(*) AS transaction_count
    FROM transactions
    WHERE date > (
        SELECT MAX(snapshot_date) - INTERVAL '90 days'
        FROM customer_snapshots
    )
    AND date <= (
        SELECT MAX(snapshot_date)
        FROM customer_snapshots
    )
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.age,
    c.location,
    c.income_bracket,
    ts.transaction_count,
    ts.total_transaction_value
FROM latest_customers c
INNER JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
WHERE c.churn = 1
ORDER BY ts.total_transaction_value DESC
LIMIT 20;

-- Which customer segments have the highest churn-related transaction exposure?

WITH transaction_summary AS (
    SELECT
        customer_id,
        SUM(amount) AS total_transaction_value
    FROM transactions
    WHERE date > (
        SELECT MAX(snapshot_date) - INTERVAL '90 days'
        FROM customer_snapshots
    )
    AND date <= (
        SELECT MAX(snapshot_date)
        FROM customer_snapshots
    )
    GROUP BY customer_id
)
SELECT
    c.income_bracket,
    COUNT(*) AS churned_customers,
    SUM(COALESCE(ts.total_transaction_value, 0))
        AS total_transaction_value
FROM latest_customers c
LEFT JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
WHERE c.churn = 1
GROUP BY c.income_bracket
ORDER BY total_transaction_value DESC;

-- What is the risk-weighted transaction value across customer segments?

WITH transaction_summary AS (
    SELECT
        customer_id,
        SUM(amount) AS total_transaction_value
    FROM transactions
    WHERE date > (
        SELECT MAX(snapshot_date) - INTERVAL '90 days'
        FROM customer_snapshots
    )
    AND date <= (
        SELECT MAX(snapshot_date)
        FROM customer_snapshots
    )
    GROUP BY customer_id
)
SELECT
    c.acquisition_channel,
    COUNT(*) AS customer_count,
    SUM(COALESCE(ts.total_transaction_value, 0))
        AS total_transaction_value,
    SUM(
        COALESCE(ts.total_transaction_value, 0) * c.churn
    ) AS churn_weighted_transaction_value
FROM latest_customers c
LEFT JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
GROUP BY c.acquisition_channel
ORDER BY churn_weighted_transaction_value DESC;

-- Which acquisition channels have the highest churn rates and transaction exposure?

WITH transaction_summary AS (
    SELECT
        customer_id,
        SUM(amount) AS total_transaction_value
    FROM transactions
    WHERE date > (
        SELECT MAX(snapshot_date) - INTERVAL '90 days'
        FROM customer_snapshots
    )
    AND date <= (
        SELECT MAX(snapshot_date)
        FROM customer_snapshots
    )
    GROUP BY customer_id
)
SELECT
    c.acquisition_channel,
    COUNT(*) AS total_customers,
    SUM(c.churn) AS churned_customers,
    ROUND(
        100.0 * SUM(c.churn) / COUNT(*),
        2
    ) AS churn_rate,
    SUM(
        CASE
            WHEN c.churn = 1
            THEN COALESCE(ts.total_transaction_value, 0)
            ELSE 0
        END
    ) AS churned_transaction_value
FROM latest_customers c
LEFT JOIN transaction_summary ts
    ON c.customer_id = ts.customer_id
GROUP BY c.acquisition_channel
ORDER BY churn_rate DESC;

-- Rank customers by transaction value within each location.

WITH transaction_summary AS (
    SELECT
        customer_id,
        SUM(amount) AS total_transaction_value
    FROM transactions
    GROUP BY customer_id
),
customer_values AS (
    SELECT
        c.customer_id,
        c.location,
        c.churn,
        COALESCE(ts.total_transaction_value, 0)
            AS total_transaction_value
    FROM latest_customers c
    LEFT JOIN transaction_summary ts
        ON c.customer_id = ts.customer_id
)
SELECT
    customer_id,
    location,
    churn,
    total_transaction_value,
    RANK() OVER (
        PARTITION BY location
        ORDER BY total_transaction_value DESC
    ) AS location_rank
FROM customer_values
ORDER BY location, location_rank;

-- Identify customers whose monthly transaction value declined compared with the previous month.

WITH monthly_transactions AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', date)::DATE AS transaction_month,
        SUM(amount) AS monthly_transaction_value
    FROM transactions
    GROUP BY
        customer_id,
        DATE_TRUNC('month', date)
),
monthly_comparison AS (
    SELECT
        customer_id,
        transaction_month,
        monthly_transaction_value,
        LAG(monthly_transaction_value) OVER (
            PARTITION BY customer_id
            ORDER BY transaction_month
        ) AS previous_month_value
    FROM monthly_transactions
)
SELECT
    customer_id,
    transaction_month,
    previous_month_value,
    monthly_transaction_value,
    previous_month_value - monthly_transaction_value
        AS decline_in_value
FROM monthly_comparison
WHERE monthly_transaction_value < previous_month_value
ORDER BY decline_in_value DESC
LIMIT 50;

-- What percentage of total transaction value does each customer contribute?

WITH customer_transactions AS (
    SELECT
        customer_id,
        SUM(amount) AS total_transaction_value
    FROM transactions
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_transaction_value,
    ROUND(
        100.0 * total_transaction_value /
        SUM(total_transaction_value) OVER (),
        4
    ) AS percentage_of_total_value
FROM customer_transactions
ORDER BY total_transaction_value DESC
LIMIT 50;

-- Divide customers into transaction-value deciles and compare their churn rates.

WITH transaction_summary AS (
    SELECT
        customer_id,
        SUM(amount) AS total_transaction_value
    FROM transactions
    GROUP BY customer_id
),
customer_deciles AS (
    SELECT
        c.customer_id,
        c.churn,
        COALESCE(ts.total_transaction_value, 0)
            AS total_transaction_value,
        NTILE(10) OVER (
            ORDER BY COALESCE(ts.total_transaction_value, 0) DESC
        ) AS value_decile
    FROM latest_customers c
    LEFT JOIN transaction_summary ts
        ON c.customer_id = ts.customer_id
)
SELECT
    value_decile,
    COUNT(*) AS customer_count,
    SUM(churn) AS churned_customers,
    ROUND(
        100.0 * SUM(churn) / COUNT(*),
        2
    ) AS churn_rate,
    ROUND(AVG(total_transaction_value), 2)
        AS average_transaction_value
FROM customer_deciles
GROUP BY value_decile
ORDER BY value_decile;