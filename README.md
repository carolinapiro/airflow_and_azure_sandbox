# Introduction to the project
The purpose of this small sandbox project is to use Airflow to automate file uploads to a Machine Learning module's database.
That module, accessible via a REST API, anwsers topic-specific questions about the files in its database.

Astronomer is used to manage the Airflow instance.

Othe technologies used are: Azure SQL Database and Azure Blob Storage.

# Solution structure

## Airflow Resources
### Connections
### Variables

# Considerations

## Idempotency

- sql: query files with in blob status before sending to the API
- send to api and update database within the same for

## Retries
