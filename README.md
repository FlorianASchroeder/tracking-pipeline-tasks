# Tracking pipeline

## Initial considerations

The goal of this project is to track events coming from an HTTP microservice to track events coming from multiple applications and to submit them to a data lake.
The pipeline shall be able to handle a fluctuating rate of events, between 500 events per second to 4000 events per second.
The payload size is between 0.5KB - 4KB.
The payload is a flat structure of string key/value pairs with many common fields, but also custom fields depending on the application sending the events.
The data freshness required is a trailing 1hr window.
### Preliminary Questions to assess
* Shall the HTTP microservice be implemented as well? 
  * I guess the firehose client is meant to be used as a package and will be deployed on AWS lambda as part of the microservice
  * -> assumption: no
* What is the name of the stream to be created and used? 
  * -> define as config from env var
* what will be the destination?
  * assumption: S3 for now as that can support Redshift and Athena for subsequent analysis
