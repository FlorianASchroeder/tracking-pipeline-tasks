# How to use


### Prerequisites
In order to package your dependencies locally with `serverless-python-requirements`, you need to have `Python3.10` installed locally.

```sh
# from repo root
cd tracker-app
sudo chown -R 1000:1000 "/home/vscode/.npm" # fix root-owned cache folder
npm install
poetry install
```

### Deployment
```sh
# for local testing
sls offline

curl -X 'POST' \
      'http://localhost:3000/track' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{ 
      "event_type": "page_view",
      "user_id": "user-1",
      "page": "home"
    }'

# for deployment
sls deploy
```

After deploy you should see output similar to:
```sh
Deploying tracker-app to stage dev (eu-central-1)

✔ Service deployed to stack tracker-app-dev (134s)

endpoints:
  POST - https://qvjxdk1smi.execute-api.eu-central-1.amazonaws.com/track
  GET - https://qvjxdk1smi.execute-api.eu-central-1.amazonaws.com/health
functions:
  tracker: tracker-app-dev-tracker (68 MB)
```

The tracking can be tested e.g. using curl:
```sh
export API_ID=qvjxdk1smi
curl -X 'POST' \
      "https://${API_ID}.execute-api.eu-central-1.amazonaws.com/track" \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "event_type": "page_view",
      "user_id": "user-1",
      "page": "home"
    }'

# or with load testing
bash load_test.sh &
```

### Cleanup
```sh
sls remove
```
