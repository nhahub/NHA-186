COPY(WITH first_per_customer AS (
    SELECT DISTINCT ON (y_m, c_id)
        m_code,
        y_m,
        c_id,
        pt4,
        esthlak,
        kest_most_faw,
        ras_kest_faw,
        kest_bank,
        ras_kest_bank,
        ez_flg1,
        total_faw,
        in_date,
        rn
    FROM customer_data
    ORDER BY y_m, c_id, rn     
),
randomized AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY y_m ORDER BY random()) AS rnd_rank
    FROM first_per_customer
)
SELECT
    m_code,
    y_m,
    c_id AS C_ID,
    TO_CHAR(TO_DATE(in_date, 'DD/MM/YY'), 'DD/MM/YYYY') AS invoice_payment_date,
    esthlak AS consumption,
    kest_most_faw AS installment_most_faw,
    ras_kest_faw AS remaining_installments_faw,
    kest_bank AS bank_installment,
    ras_kest_bank AS remaining_bank_installments,
    ez_flg1 AS customer_type,
    total_faw AS total_financial_amount,
    TO_CHAR(TO_DATE(pt4, 'DD/MM/YY'), 'DD/MM/YYYY') AS contract_date
FROM randomized
WHERE rnd_rank <= 20000
ORDER BY y_m, rnd_rank
)TO 'C:/Users/amet1/Downloads/.Courses/DEPI/final project/PT/output.csv'
WITH (FORMAT CSV, HEADER, ENCODING 'UTF8');
