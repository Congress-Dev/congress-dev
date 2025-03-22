SELECT *
FROM public.legislation_action_parse
WHERE
    legislation_version_id = 73910;


    SELECT lap.*
    FROM public.legislation_action_parse lap
    LEFT JOIN public.usc_content_diff ucd
      ON lap.legislation_content_id = ucd.legislation_content_id
    WHERE ucd.legislation_content_id IS NULL
    AND lap.legislation_version_id = 73910
      AND cardinality(lap.actions) >= 1
      AND cardinality(lap.citations) >= 1;