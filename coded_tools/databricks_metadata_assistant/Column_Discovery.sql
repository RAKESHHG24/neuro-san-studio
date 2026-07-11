SELECT
  column_name,
  data_type,
  comment
FROM system.information_schema.columns
WHERE table_catalog = '{catalog}'
AND table_schema = '{schema}'
AND table_name = '{table}';