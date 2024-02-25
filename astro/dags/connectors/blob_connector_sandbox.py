
from typing import List
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
import json

class BlobConnector():

    # Class attributes
    _blob_conn_id = "Blob_Sandbox"
    _container = "blob-sandbox"
    _container_path = "https://sandboxaccount.blob.core.windows.net/blob-sandbox/"
    _account_name = "sandboxaccount"

    def __init__(self):
        # Instance attributes
        self._blob_hook = None
        

    # Methods

    def connect_to_blob_storage(self):
        """Create the Hook to connect to the Blob Storage"""

        self._blob_hook = WasbHook(wasb_conn_id = BlobConnector._blob_conn_id)


    def query_blob_file_list(self):
        """Return the list of file names in the container"""

        file_list = self._blob_hook.get_blobs_list(container_name= BlobConnector._container)
        return file_list
    

    def add_links_to_file_list(self, file_list: List[str]) -> dict:
        """Form the list of files in the container to be inserted in the database"""

        file_dict = []
        for f in file_list:
            file_dict.append({"file_name": f, 
                              "link_to_blob_file": BlobConnector._container_path + f})
        return file_dict
    

    def build_data_for_API_upload(self, file_dict: dict) -> List[dict]:
        """Form the list of files to be uploaded into the ML API"""
        
        file_data = []
        for f in file_dict:
            f_to_api = {"account_name": BlobConnector._account_name,
                        "container_name": BlobConnector._container,
                        "path": f["file_name"]}
            f_to_api = json.dumps(f_to_api, indent=4)
            file_data.append(f_to_api)

        return file_data