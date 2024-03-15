# AWS Infrastructure for Firehose tracker

This terraform configuration sets up all AWS infrastructure components required to run the firehose tracker.
Before creation of resources, deploy [firehose-transformations](../firehose-transformations/README.md) and update the ARN together with version number in the [variables.tf](variables.tf).

```sh
# to be executed from git root
cd tracker-infra

# ensure credentials are loaded, e.g. through env-vars
export AWS_ACCESS_KEY_ID=XXX
export AWS_SECRET_ACCESS_KEY=XXX

# initialise 
terraform init

# inspect resources to be created
terraform plan

# Create or update resources
terraform apply -auto-approve

# Get relevant outputs
terraform output
# or pipe into .env file
terraform output | sed 's/\s*=\s*/=/g' > ../tracker-app/.env
# or set them as env variables
export $(terraform output | sed 's/\s*=\s*/=/g' | xargs)


# Remove all resources
terraform destroy
```

After creation of resources, use names and arns to configure the [firehose_tracker](../firehose_tracker/firehose_tracker/config.py)
