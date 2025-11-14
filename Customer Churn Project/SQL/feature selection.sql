CREATE OR REPLACE VIEW churn_features AS
SELECT
    age,
    tenure,
    usage_frequency,
    support_calls,
    payment_delay,
    subscription_type,
    contract_length,
    total_spend,
    last_interaction,
    churn
FROM customer_churn;

