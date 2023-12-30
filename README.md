# Introduction to the project
The purpose of this small sandbox project is to use Airflow to automate file uploads to a Machine Learning module's database.
That module, accessible via a REST API, anwsers topic-specific questions about the files in its database.

Astronomer is used to manage the Airflow instance.

Othe technologies used are: Azure SQL Database and Azure Blob Storage.

# Solution structure
The code for this solution is in the dags folder, divided in 4 files:

- In the connectors subfolder:
  One file for each external resource used: ML API, Azure SQL Database and Azure Blob Storage.
  In each of them, there are:
  - class attributes for common information, such as the connection id, container id, etc.
  - instance attributes for the hook used.
  - methods to initialize the hook and perform operations in the resources, such as query a table, use a REST endpoint, etc.

- The dag file:
  - task definitions
  - dag definition
    
## Tasks Logic

- **new_files_branch**:
  It queries the list of files in the blob storage, and compares its length with the number of files in the storage from the previous run.
  If the number of files currently available in the blob storage hasn't increased, the dag run ends.
- **identify_new_files**:
  The list of files in the blob storage and database are compared, and the nwely added files in the blob storage are identified.
- **add_new_files_to_database**:
  These new files are added to the database, and the number of files for future runs is updated.
- **upload_files_to_ML_API**:
  The files are formatted and loaded into the API, and their status is updated accordingly in the database. 
- **end**:
  Dummy task to identify the end of the process.

## Airflow Resources
Connections to the ML API, Azure SQL Database and Azure Blob Storage were configured in the Airflow UI.
Also, some variables were defined in the UI too, to save the number of files that were found in the Blob Storage in previous runs of the DAG.

### Connections
- id: "Http_Sandbox", type: HTTP
  host also specified.
- id: "Blob_Sandbox", type: Azure Blob Storage (wasb)
  blob storage login and key also specified.
- id: "SQL_Sandbox", type: Microsoft SQL Server (mssql)
  host, schema, login, password and port also specified.

### Variables
- count_files_in_blob
- count_files_in_blob_stg

# Considerations
Some considerations were made in the code regarding the idempotency of the tasks, as well as the number of times each of them sould be retried.

## Idempotency

- **upload_files_to_ML_API**:
  The files to be updated to the API (with "in blob" status) is queried from the database, before sending them to the API,
  to avoid any retries on this task allows to re-upload duplicated files.
  One case in which an already uploaded file can be uploaded again is when the *send_upload_request(f)* method succeeded, but not the
  *update_status_for_uploaded_files(f['path'])* one. But, in tbis example, we do not have access to an endpoint in the API to check the files already
  uploaded in it.
  
- **upload_files_to_ML_API**:
  The files are sent to the API and the database status is updated within the same for because, in case one of the inserts fails, only its status won't
  be updated.

## Retries

The default retry number for each task is defined as 1, but for some tasks this number was overwritten:

- **add_new_files_to_database**:
  It has 0 retries because we prefer to re-start the whole dag again in case of failure.
  The event of the database connection not being successful is unlikely, given that it was successful in the previous tasks,
  but the insert statement could also fail, and it could fail on any file. So, the files_dict calculated in the previous task may not be accurate on a second run
  of the task, it could contain files that were already inserted in the database.
  Changes can be made to the dag logic to prevent this, but we preferred the simplicity of the current logic, and we think the insert errors won't be frequent.
  
- **upload_files_to_ML_API**:
  It has 3 retries because, in this case, this is a resource we have no control over.
  It is assumed that the API could be unstable, and having an error as response the first times could not mean the resource is not available permanently.
  The endpoint calls are not costly in time, so we can afford to retry some more times.
  This may be re-evaluated as the dag runs for some time, and it may be the case that the API only errors out when there is a recurrent problem, so the number of
  retries should be smaller.

# Astronomer and Airflow Related Info

Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

## Project Contents

Your Astro project contains the following files and folders:

- dags: This folder contains the Python files for your Airflow DAGs.
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains any additional files that you want to include as part of your project. It is empty by default.
- packages.txt: Install OS-level packages needed for your project by adding them to this file. It is empty by default.
- requirements.txt: Install Python packages needed for your project by adding them to this file. It is empty by default.
- plugins: Add custom or community plugins for your project to this file. It is empty by default.
- airflow_settings.yaml: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project.

## Deploy Your Project Locally

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 4 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks

2. Verify that all 4 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start your project with the Airflow Webserver exposed at port 8080 and Postgres exposed at port 5432. If you already have either of those ports allocated, you can either [stop your existing Docker containers or change the port](https://docs.astronomer.io/astro/test-and-troubleshoot-locally#ports-are-not-available).

3. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.

You should also be able to access your Postgres Database at 'localhost:5432/postgres'.

## Deploy Your Project to Astronomer

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deploying instructions, refer to Astronomer documentation: https://docs.astronomer.io/cloud/deploy-code/
