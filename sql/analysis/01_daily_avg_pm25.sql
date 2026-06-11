-- Daily average PM2.5 for Kossutha station
-- Sorted by highest pollution days

SELECT
	timestamp::DATE AS day,
	ROUND(AVG(value)::NUMERIC, 2) AS pm2_5
FROM measurements
WHERE station = 'kossutha'
	AND parameter = 'pm25'
GROUP BY day
ORDER BY pm2_5 DESC
LIMIT 10;
