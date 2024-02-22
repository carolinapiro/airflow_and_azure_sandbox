
from airflow.providers.http.hooks.http import HttpHook

class ApiConnector:

    # Class attributes
    _api_conn_id = "Http_Sandbox"

    def __init__(self):
        # Instance attributes
        self._http_hook = None


    # Methods

    def connect_to_ml_api(self):
        """Connect to the ML API"""

        self._http_hook = HttpHook(http_conn_id = ApiConnector._api_conn_id,
                                   method="POST" )


    def send_upload_request(self, file_data):
        """Upload the file in the ML API"""

        endpoint_string = "upload_file/"

        self._http_hook.run(endpoint = endpoint_string,
                            data = file_data,
                            headers = {"Content-Type":"application/json"})
