SELECT 1 as user_id, 1 as ts_min_index, 's1' as session_id
UNION ALL
SELECT 1 as user_id, 2 as ts_min_index, 's1' as session_id
UNION ALL
-- should be grouped with previous session
SELECT 1 as user_id, 22 as ts_min_index, 's2' as session_id
UNION ALL
-- more than 30 minutes passed, should be considered a new session
SELECT 1 as user_id, 60 as ts_min_index, 's2' as session_id
UNION ALL
SELECT 2 as user_id, 4 as ts_min_index, 's3' as session_id
UNION ALL
-- more than 30 minutes passed, should be considered a new session
SELECT 2 as user_id, 44 as ts_min_index, 's3' as session_id
