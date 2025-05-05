# right now i intend to create a class with a few methods to control
# resources (add/delete/edit) here, if this gets too complicated i may decide to
# split it into seperate files

# this contains mostly code written by Connor found in Python_Scripts.zip in the Onedrive.
# i am mostly writing wrappers and making the code a little more abstract and generally usable

from eln_packages_common import config
from typing import Any
import json
import requests
import pandas as pd

class Resource_Manager:
    def __init__(self):
        self.itemsapi = config.load_items_api()
        self.expapi = config.load_experiments_api()
        self.uploadsapi = config.load_uploads_api()
        self.printer_path = config.PRINTER_PATH  # this is the path where the labels will be saved, it is set in the config file, and accessed in printer/generate_label.py

    def create_item(self, category: int, body_dict: dict[str, Any]):
        response = self.itemsapi.post_item_with_http_info( # type: ignore
            body={
                "category_id": category,
            }
        ) 
        locationHeaderInResponse: str = str(response[2].get("Location")) #type: ignore
        print(f"The newly created item is here: {locationHeaderInResponse}")
        item_id:int = int(locationHeaderInResponse.split("/").pop())
        self.change_item(item_id, body_dict)

    def change_item(self, id: int, body_dict: dict[str, Any]):
        self.itemsapi.patch_item(id, body=body_dict) #type: ignore

    def upload_file(
        self, id:int, path:str, comment:str="", resource_type:str="items"
    ):  # resource_type can be 'item' or 'experiment', wraps the upload api
        self.uploadsapi.post_upload(resource_type, id, file=path, comment=comment) #type: ignore
    def post_url(self,url:str) -> requests.Response:
        header:dict[str,str] = config.api_client.default_headers
        header = {**header, **{"Content-type": "application/json"}}
        url = config.URL + url
        return requests.post(url, headers=header)
    def experiment_item_link(self, experiment_id: int, item_id: int):
        url = (
            "/experiments/"
            + str(experiment_id)
            + "/items_links/"
            + str(item_id)
        )
        # checks if the resource and experiment exist, throws error if not
        try:
            self.get_item(item_id)
            self.get_experiment(experiment_id)
        except config.elabapi_python.rest.ApiException:
            raise ValueError("Experiment or item does not exist")
        self.post_url(url)
    def add_tag(self, item_id: int, tag: str):
        header = config.api_client.default_headers
        header = {**header, **{"Content-type": "application/json"}}
        url = config.URL + "/items/" + str(item_id) + "/tags/"
        requests.post(url, headers=header, json={"tag": tag})

    def delete_upload(
        self, id:int, upload_id:int, resource_type:str="items"
    ):  # resource_type can be 'item' or 'experiment', wraps the upload api
        self.uploadsapi.delete_upload(resource_type, id, upload_id) #type: ignore   
    def get_metadata(self, id:int) -> dict[str, Any]:
        return json.loads(self.get_item(id)["metadata"])
    
    def get_item(self, id:int) -> dict[str, Any]:
        return self.itemsapi.get_item(id).to_dict() #type: ignore
        # this dictionary should contain:
        # title, id, category, metadata, rating
        # a lot of items are contained in the metadata field, which is a json string
        # this can be easily converted to/from a python dictionary in any method used to edit metadata
    def get_experiment(self, id:int) -> dict[str, Any]:
        return self.expapi.get_experiment(id).to_dict()

    def get_items_types(self) -> list[dict[str,Any]]: 
        header = config.api_client.default_headers
        header = {**header, **{"Content-type": "application/json"}}
        # construct full API URL
        url = (
            config.URL
            + "/items_types"
        )
        return requests.get(url, headers=header).json()

    def get_items(self, size:int=15, return_dict=False) -> list[object]: #TODO: figure out this type situation i hate it
        # returns the most recent 15 if a size is not specified
        header = config.api_client.default_headers
        header = {**header, **{"Content-type": "application/json"}}
            # construct full API URL
        url = (
            config.URL
            + "/items?limit="
            + str(size)
        )
        return requests.get(url, headers=header).json()
    def get_experiments(self) -> list[object]:
        return self.expapi.read_experiments() #type: ignore

    def get_uploaded_files(self, id:int, resource_type:str="items") -> list:
        return self.uploadsapi.read_uploads( #type: ignore
            resource_type, id
        )  # returns a list of file objects that can be written to a file
    
    def get_items_df(self, size=15):
        def json_loads(x): # function to get dictionaries from json, accounting for elements that may be dictionaries already, json strings, or None
            if isinstance(x, dict):
                return x
            if isinstance(x, str):
                try:
                    return json.loads(x)
                except json.JSONDecodeError:
                    return {}
            return {}

        def flatten_extra_fields(extra): # function to flatten the extra_fields dictionary
            if not isinstance(extra, dict):
                return {}
            return {k: v.get('value') for k, v in extra.items() if isinstance(v, dict)}
        
        df: pd.DataFrame = pd.DataFrame(self.get_items(size, return_dict=True))
        df['metadata'] = df['metadata'].apply(json_loads)
        metadata: pd.DataFrame = df['metadata'].apply(pd.Series)
        extra_fields_df: pd.DataFrame = metadata['extra_fields'].apply(flatten_extra_fields).apply(pd.Series)
        df = pd.concat([df.drop(columns='metadata'), metadata.drop(columns='extra_fields'), extra_fields_df], axis=1)
        return df