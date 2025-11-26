CREATE OR REPLACE VIEW customer_view AS
SELECT 
    m_code,
    y_m as due_invoice_date,
    TO_CHAR(TO_DATE(pt4, 'DD/MM/YY'), 'YYYY-MM-DD') AS contract_date,
    esthlak AS consumption,
    kest_most_faw AS last_financial_installment,
    ras_kest_faw AS remaining_financial_installments,
    kest_bank AS bank_installment,
    ras_kest_bank AS remaining_bank_installments,
    ez_flg1 AS customer_type,
    total_faw AS total_financial_amount,
    TO_CHAR(TO_DATE(in_date, 'DD/MM/YY'), 'YYYY-MM-DD') AS invoice_payment_date,
    CASE 
        WHEN amel_s IN (2, 22, 23, 33, 34, 44) THEN '0'
        ELSE '1'
    END AS payment_status
FROM customer_data
