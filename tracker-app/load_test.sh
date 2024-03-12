#!/bin/bash

# spawn 2000 requests to the API per process
for i in {1..2000}
do
  curl -X 'POST' \
    "https://${API_ID}.execute-api.eu-central-1.amazonaws.com/track" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d "{
    \"event_type\": \"page_view\",
    \"user_id\": \"user-${i}\",
    \"page\": \"home\"
  }" &
done
