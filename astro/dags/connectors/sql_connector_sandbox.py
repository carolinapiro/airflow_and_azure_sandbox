
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook

from datetime import datetime

class SQLConnector():

    # Class attributes
    _sql_conn_id = "SQL_Sandbox"


    def __init__(self):
        # Instance attributes
        self._sql_hook = None


    # Methods

    def connect_to_sql_database(self):
        """Create the Hook to connect to the Azure Database"""

        self._sql_hook = MsSqlHook(mssql_conn_id = SQLConnector._sql_conn_id)


    def query_database_processed_files(self):
        """Query the list of files in the database"""
        file_list = self._sql_hook.get_pandas_df(sql="SELECT DISTINCT file_name FROM processed_file")
        return file_list["file_name"].tolist()


    def query_database_to_upload_files(self):
        """Query the list of files with 'in blob' status in the database"""

        file_list = self._sql_hook.get_pandas_df(sql="SELECT DISTINCT file_name FROM processed_file WHERE file_status = 'in blob'")
        return file_list["file_name"].tolist()


    def insert_new_files(self, files_dict):
        """Insert new unprocessed files in the database"""

        sql_query = f"INSERT INTO processed_file (file_name, link_to_blob_file, file_status, file_date) VALUES "
        for file in files_dict:
            file_values = f"('{file['file_name']}', '{file['link_to_blob_file']}', 'in blob', '{str(datetime.now()).split('.')[0]}'),"
            sql_query = sql_query + file_values
        sql_query = sql_query[:len(sql_query) - 1]
        
        self._sql_hook.run(sql= sql_query)


    def update_status_for_uploaded_files(self, file):
        """Update processed files in the database"""

        sql_query = f"UPDATE processed_file SET file_status = 'in api' WHERE file_name = '{file}';"
        self._sql_hook.run(sql= sql_query)


