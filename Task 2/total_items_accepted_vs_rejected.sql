SELECT r.rewardsReceiptStatus, SUM(r.purchasedItemCount) AS total_items
FROM Receipts r
WHERE r.rewardsReceiptStatus IN ('Accepted', 'Rejected')
GROUP BY r.rewardsReceiptStatus;
