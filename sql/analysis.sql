-- Procurement Decision Intelligence: advanced SQL case study
-- Dialect: PostgreSQL-style ANSI SQL.
-- Assumes normalized table: purchase_card_transactions
-- Columns: objectid, agency, transaction_date, transaction_amount,
--          vendor_name, vendor_state_province, mcc_description

-- ---------------------------------------------------------------------------
-- 1) Agency operating profile
-- ---------------------------------------------------------------------------
SELECT
    agency,
    COUNT(*) AS transaction_count,
    SUM(ABS(transaction_amount)) AS absolute_spend,
    AVG(ABS(transaction_amount)) AS avg_abs_transaction,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(transaction_amount)) AS median_abs_transaction,
    MAX(ABS(transaction_amount)) AS max_abs_transaction,
    COUNT(DISTINCT vendor_name) AS vendor_count,
    COUNT(DISTINCT mcc_description) AS mcc_count
FROM purchase_card_transactions
GROUP BY agency
ORDER BY absolute_spend DESC;

-- ---------------------------------------------------------------------------
-- 2) Near-duplicate pattern using LAG
-- Same agency/vendor/amount repeated within three days.
-- ---------------------------------------------------------------------------
WITH sequenced AS (
    SELECT
        objectid,
        agency,
        vendor_name,
        transaction_amount,
        transaction_date,
        LAG(transaction_date) OVER (
            PARTITION BY agency, vendor_name, transaction_amount
            ORDER BY transaction_date
        ) AS prior_date
    FROM purchase_card_transactions
)
SELECT *,
       transaction_date - prior_date AS days_since_same_vendor_amount
FROM sequenced
WHERE prior_date IS NOT NULL
  AND transaction_date - prior_date BETWEEN INTERVAL '0 day' AND INTERVAL '3 day'
ORDER BY agency, vendor_name, transaction_date;

-- ---------------------------------------------------------------------------
-- 3) Vendor concentration + HHI by agency
-- HHI makes the portfolio more analytical than simply listing top vendors.
-- ---------------------------------------------------------------------------
WITH vendor_spend AS (
    SELECT
        agency,
        vendor_name,
        SUM(ABS(transaction_amount)) AS vendor_spend
    FROM purchase_card_transactions
    GROUP BY agency, vendor_name
), shares AS (
    SELECT
        agency,
        vendor_name,
        vendor_spend,
        vendor_spend / NULLIF(SUM(vendor_spend) OVER (PARTITION BY agency), 0) AS spend_share
    FROM vendor_spend
)
SELECT
    agency,
    SUM(POWER(spend_share, 2)) AS vendor_hhi,
    MAX(spend_share) AS largest_vendor_share,
    COUNT(*) AS vendor_count
FROM shares
GROUP BY agency
ORDER BY vendor_hhi DESC;

-- ---------------------------------------------------------------------------
-- 4) Cross-agency vendor reach
-- ---------------------------------------------------------------------------
SELECT
    vendor_name,
    COUNT(DISTINCT agency) AS agency_reach,
    COUNT(*) AS transaction_count,
    SUM(ABS(transaction_amount)) AS absolute_spend,
    MIN(transaction_date) AS first_observed_date,
    MAX(transaction_date) AS last_observed_date
FROM purchase_card_transactions
GROUP BY vendor_name
HAVING COUNT(DISTINCT agency) >= 2
ORDER BY agency_reach DESC, absolute_spend DESC;

-- ---------------------------------------------------------------------------
-- 5) Vendor monthly-spend change vs trailing six observed months
-- ---------------------------------------------------------------------------
WITH monthly AS (
    SELECT
        agency,
        vendor_name,
        DATE_TRUNC('month', transaction_date) AS month,
        SUM(ABS(transaction_amount)) AS month_spend
    FROM purchase_card_transactions
    GROUP BY agency, vendor_name, DATE_TRUNC('month', transaction_date)
), baseline AS (
    SELECT
        *,
        AVG(month_spend) OVER (
            PARTITION BY agency, vendor_name
            ORDER BY month
            ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
        ) AS trailing_avg_spend,
        STDDEV_SAMP(month_spend) OVER (
            PARTITION BY agency, vendor_name
            ORDER BY month
            ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
        ) AS trailing_sd_spend
    FROM monthly
)
SELECT
    *,
    (month_spend - trailing_avg_spend) / NULLIF(trailing_sd_spend, 0) AS trailing_z
FROM baseline
WHERE trailing_avg_spend IS NOT NULL
ORDER BY trailing_z DESC NULLS LAST;

-- ---------------------------------------------------------------------------
-- 6) Rare agency / merchant-category combinations
-- ---------------------------------------------------------------------------
WITH combo AS (
    SELECT agency, mcc_description, COUNT(*) AS combo_count
    FROM purchase_card_transactions
    GROUP BY agency, mcc_description
), agency_total AS (
    SELECT agency, COUNT(*) AS agency_count
    FROM purchase_card_transactions
    GROUP BY agency
)
SELECT
    c.agency,
    c.mcc_description,
    c.combo_count,
    a.agency_count,
    1.0 * c.combo_count / NULLIF(a.agency_count, 0) AS combo_share
FROM combo c
JOIN agency_total a USING (agency)
WHERE 1.0 * c.combo_count / NULLIF(a.agency_count, 0) < 0.01
ORDER BY combo_share, combo_count;

-- ---------------------------------------------------------------------------
-- 7) Same-day vendor bursts with within-day value concentration
-- ---------------------------------------------------------------------------
SELECT
    agency,
    vendor_name,
    CAST(transaction_date AS DATE) AS transaction_day,
    COUNT(*) AS transactions,
    SUM(ABS(transaction_amount)) AS daily_abs_amount,
    MAX(ABS(transaction_amount)) AS max_transaction,
    MAX(ABS(transaction_amount)) / NULLIF(SUM(ABS(transaction_amount)), 0) AS largest_tx_share
FROM purchase_card_transactions
GROUP BY agency, vendor_name, CAST(transaction_date AS DATE)
HAVING COUNT(*) >= 3
ORDER BY transactions DESC, daily_abs_amount DESC;

-- ---------------------------------------------------------------------------
-- 8) Newly observed agency/vendor relationships by monthly cohort
-- This means new in the available dataset window, not necessarily new supplier onboarding.
-- ---------------------------------------------------------------------------
WITH first_seen AS (
    SELECT
        agency,
        vendor_name,
        MIN(transaction_date) AS first_seen_date
    FROM purchase_card_transactions
    GROUP BY agency, vendor_name
)
SELECT
    DATE_TRUNC('month', first_seen_date) AS observed_relationship_cohort,
    COUNT(*) AS newly_observed_relationships
FROM first_seen
GROUP BY DATE_TRUNC('month', first_seen_date)
ORDER BY observed_relationship_cohort;

-- ---------------------------------------------------------------------------
-- 9) Pareto analysis: how many vendors explain 80% of agency spend?
-- ---------------------------------------------------------------------------
WITH vendor_spend AS (
    SELECT agency, vendor_name, SUM(ABS(transaction_amount)) AS vendor_spend
    FROM purchase_card_transactions
    GROUP BY agency, vendor_name
), ranked AS (
    SELECT
        *,
        vendor_spend / NULLIF(SUM(vendor_spend) OVER (PARTITION BY agency), 0) AS spend_share,
        SUM(vendor_spend) OVER (
            PARTITION BY agency ORDER BY vendor_spend DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) / NULLIF(SUM(vendor_spend) OVER (PARTITION BY agency), 0) AS cumulative_share
    FROM vendor_spend
)
SELECT
    agency,
    COUNT(*) FILTER (WHERE cumulative_share - spend_share < 0.80) AS vendors_to_reach_80pct,
    COUNT(*) AS total_vendors
FROM ranked
GROUP BY agency
ORDER BY vendors_to_reach_80pct;
