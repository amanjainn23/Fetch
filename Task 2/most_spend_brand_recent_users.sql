SELECT b.name AS brand_name, SUM(r.totalSpent) AS total_spent
FROM Receipts r
JOIN Users u ON r.userId = u._id
JOIN Brands b ON r.brandId = b._id
WHERE u.createdDate >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY b.name
ORDER BY total_spent DESC
LIMIT 1;
