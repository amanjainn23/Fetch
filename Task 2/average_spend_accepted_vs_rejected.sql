SELECT r.rewardsReceiptStatus, AVG(r.totalSpent) AS avg_spend
FROM Receipts r
WHERE r.rewardsReceiptStatus IN ('Accepted', 'Rejected')
GROUP BY r.rewardsReceiptStatus;
