SELECT b.name AS brand_name, COUNT(r._id) AS transaction_count
FROM Receipts r
JOIN Users u ON r.userId = u._id
JOIN Brands b ON r.brandId = b._id
WHERE u.createdDate >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY b.name
ORDER BY transaction_count DESC
LIMIT 1;
