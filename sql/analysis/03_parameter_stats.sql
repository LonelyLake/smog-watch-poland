-- Statistics by parameter
-- Number of values, min, max, average, median

SELECT
	parameter,
	COUNT(value) AS count_values,
	MIN(value) AS min_value,
	MAX(value) AS max_value,
	ROUND(AVG(value)::NUMERIC, 2) AS avg_value,
	ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value)::NUMERIC, 2) AS median_value
FROM measurements
WHERE station = 'kossutha'
GROUP BY parameter
ORDER BY parameter;
