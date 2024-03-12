import duckdb

con = duckdb.connect("../session_data.duckdb")
out = con.sql("select * from fixed order by user_id, ts_min_index")
print(out)
