-- Active: 1737907031710@@10.0.0.248@5432@us_code_2023@public


-- Find action parses that didn't produce a diff
SELECT 
  lap.*
FROM 
  legislation_action_parse lap
LEFT JOIN 
  usc_content_diff ucd
ON 
  lap.legislation_content_id = ucd.legislation_content_id
WHERE 
  ucd.legislation_content_id IS NULL
AND 
  lap.legislation_version_id = 73910
AND 
  array_length(lap.citations, 1) > 0;