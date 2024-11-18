SELECT b.name AS brand_name, COUNT(r._id) AS receipt_count
FROM Receipts r
JOIN Brands b ON r.brandId = b._id
WHERE DATE_TRUNC('month', r.dateScanned) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
GROUP BY b.name
ORDER BY receipt_count DESC
LIMIT 10;
