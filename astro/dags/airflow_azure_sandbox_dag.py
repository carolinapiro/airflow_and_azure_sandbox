from airflow.decorators import dag, task

from connectors.blob_connector_sandbox import BlobConnector
from connectors.sql_connector_sandbox import SQLConnector
from connectors.api_connector_sandbox import ApiConnector

from airflow.operators.empty import EmptyOperator
from airflow.models import Variable

from datetime import datetime, timedelta


# ---------- TASKS DEFINITION ----------

@task.branch
def new_files_branch():

    # Connect to the Blob Storage
    blob_connector = BlobConnector()
    blob_connector.connect_to_blob_storage()

    # Obtain the list of files in the Blob Storage, and count them
    blob_files = blob_connector.query_blob_file_list()
    count = len(blob_files)

    # Chech if there are new files
    if count > int(Variable.get("count_files_in_blob")):
        # Save new number of files and Continue running the DAG
        Variable.set(key = "count_files_in_blob_stg", value = count)
        return "identify_new_files"
    else: 
        # End the DAG run
        return "end"


@task.python
def identify_new_files():
    
    # Connect to Database and Blob Storage
    sql_connector = SQLConnector()
    sql_connector.connect_to_sql_database()
    blob_connector = BlobConnector()
    blob_connector.connect_to_blob_storage()

    # Obtain list of files in the SQL Database and Blob Storage
    sql_files = sql_connector.query_database_processed_files()
    blob_files = blob_connector.query_blob_file_list()

    # Compare the lists and identify new files
    new_files = set(blob_files)-set(sql_files)

    # Create the dataset to be inserted in the database
    new_files_dict = blob_connector.add_links_to_file_list(new_files)

    return new_files_dict


@task.python(retries = 0)
def add_new_files_to_database(files_dict):

    # Connect to SQL Database
    sql_connector = SQLConnector()
    sql_connector.connect_to_sql_database()

    # Insert rows for the new files
    sql_connector.insert_new_files(files_dict)

    # Update Blob files count
    count = Variable.get("count_files_in_blob_stg")
    Variable.set(key = "count_files_in_blob", value = count)


@task.python(retries = 3)
def upload_files_to_ML_API():

    # Connect to Database and API, and intanciate a Blob Connector
    api_connector = ApiConnector()
    api_connector.connect_to_ml_api()
    sql_connector = SQLConnector()
    sql_connector.connect_to_sql_database()
    blob_connector = BlobConnector()
    
    # Query files to be uploaded
    files_to_upload = sql_connector.query_database_to_upload_files()
    # Create the dataset to be uploaded into the API
    file_dict = blob_connector.add_links_to_file_list(files_to_upload)

    # Build the payload for the API request
    files_data = blob_connector.build_data_for_API_upload(file_dict)
    
    for f in files_data:
        # Send the upload request to the API for the new files
        api_connector.send_upload_request(f)

        # Update the status of the uploaded files in the SQL Database
        sql_connector.update_status_for_uploaded_files(f['path'])


# ---------- DAG DEFINITION ----------

default_args = {"retries": 1, "retry_delay": timedelta(seconds=10)}

@dag( start_date= datetime(2023, 9, 1), schedule= timedelta(hours=4), catchup= False,
      default_args= default_args )
def airflow_azure_sandbox_dag():

    # Tasks

    identify_new_files_result = identify_new_files()
    end = EmptyOperator(task_id = "end", trigger_rule="none_failed_min_one_success")

    # Dependencies
    
    new_files_branch() >> [identify_new_files_result, end]
    add_new_files_to_database(identify_new_files_result) >> upload_files_to_ML_API() >> end


airflow_azure_sandbox_dag()



