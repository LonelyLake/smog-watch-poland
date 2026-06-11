-- Days exceeding WHO PM2.5 daily limit
-- WHO 2021 guideline: 24-hour mean should not exceed 15 µg/m³
-- Note: No exceedances expected in summer months - run with winter data for results

SELECT
	timestamp::DATE AS day,
	ROUND(AVG(value)::NUMERIC, 2) AS pm2_5
FROM measurements
WHERE station = 'kossutha'
	AND parameter = 'pm25'
GROUP BY day
HAVING AVG(value) > 15
ORDER BY pm2_5 DESC;
