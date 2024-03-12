WITH lagged_data AS (
  SELECT
    user_id,
    ts_min_index,
    session_id,
    ts_min_index - LAG(ts_min_index) OVER (PARTITION BY user_id ORDER BY ts_min_index) AS ts_min_diff,
    (
      ts_min_index
      - LAG(ts_min_index) OVER (PARTITION BY user_id ORDER BY ts_min_index)
    ) > 30 AS new_session_started
  FROM {{ ref("raw") }}
),

session_added AS (
  SELECT
    *,
    'u' || user_id || '.s' || COALESCE(
      SUM(new_session_started::int) OVER (PARTITION BY user_id ORDER BY ts_min_index) + 1,
      1
    ) AS new_session_id
  FROM lagged_data
)

SELECT
  user_id,
  ts_min_index,
  session_id AS old_session_id,
  new_session_id AS session_id
FROM session_added
