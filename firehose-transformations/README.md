# Firehose data transformations

This project contains nodejs-based data transformations to be used in firehose delivery streams.
In order to store `.jsonl` appropriately in S3 for subsequent analysis with AWS Athena, a newline fix has to be applied.

Deploy this component before creating resources with [tracker-infra](../tracker-infra/README.md)

## Usage

### Deployment

In order to deploy the example, you need to run the following command:

```sh
serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying firehose-transformations to stage dev (eu-central-1)

✔ Service deployed to stack firehose-transformations-dev (81s)

functions:
  fix-newline: firehose-transformations-dev-fix-newline (922 B)
```


### Cleanup

```sh
serverless remove
```
