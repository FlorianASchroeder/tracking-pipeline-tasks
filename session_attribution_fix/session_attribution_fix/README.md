# Session Attribution Fix

The purpose of this small DBT project is to demonstrate how session attribution might be fixed within a DBT pipeline.
In order to get started, perform the following:

```sh
# assume starting in repository root
cd session_attribution_fix
# install required packages and activate environment
poetry install
cd session_attribution_fix
# install dbt packages
dbt deps

# Run & Test models
dbt build --select raw+

# extract model information
dbt run-operation generate_model_yaml --args '{"model_names": ["raw","fixed"]}' > models.yml

# Look at table
python -m check_data
```
