WITH recent_month AS (
    SELECT b.name AS brand_name, COUNT(r._id) AS receipt_count
    FROM Receipts r
    JOIN Brands b ON r.brandId = b._id
    WHERE DATE_TRUNC('month', r.dateScanned) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
    GROUP BY b.name
    ORDER BY receipt_count DESC
    LIMIT 5
),
previous_month AS (
    SELECT b.name AS brand_name, COUNT(r._id) AS receipt_count
    FROM Receipts r
    JOIN Brands b ON r.brandId = b._id
    WHERE DATE_TRUNC('month', r.dateScanned) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '2 months')
    GROUP BY b.name
    ORDER BY receipt_count DESC
    LIMIT 5
)
SELECT recent.brand_name AS recent_brand, previous.brand_name AS previous_brand
FROM recent_month recent
FULL OUTER JOIN previous_month previous ON recent.brand_name = previous.brand_name;
