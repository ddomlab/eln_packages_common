# right now i intend to create a class with a few methods to control
# resources (add/delete/edit) here, if this gets too complicated i may decide to
# split it into seperate files

# this contains mostly code written by Connor found in Python_Scripts.zip in the Onedrive.
# i am mostly writing wrappers and making the code a little more abstract and generally usable
import eln_packages_common.config as config
from typing import Any
import json
import requests
import pandas as pd

class Resource_Manager:
    def __init__(self, key: str | None = None):
        self.itemsapi = config.load_items_api(key)
        self.expapi = config.load_experiments_api(key)
        self.uploadsapi = config.load_uploads_api(key)
        self.printer_path = config.PRINTER_PATH  # this is the path where the labels will be saved, it is set in the config file, and accessed in printer/generate_label.py
        header = config.get_api_key(key).default_headers
        self.header = {**header, **{"Content-type": "application/json"}}


    def post_url(self,url:str) -> requests.Response:
        """
        TODO: is this necessary? Either use this method everywhere or not at all
        Posts a URL to the ELN with the given URL. Used for more manual processes.
            :param str url: The URL to be posted.
        """
        url = config.URL + url
        return requests.post(url, headers=self.header)
    def get_url(self,url:str) -> requests.Response:
        """
        TODO: is this necessary? Either use this method everywhere or not at all
        Sends a GET request to the ELN with the given URL. Used for more manual processes.
            :param str url: The URL to be posted.
        """
        url = config.URL + url
        return requests.get(url, headers=self.header)
    def create_item(self, category: int, body_dict: dict[str, Any]) -> None:
        """
        Creates an item in the ELN with the given category and body_dict.
            :param int category: The category ID of the itme to be created. {1:Instument,2:Chemical Compound,3:Polymer,4:Solution}
            :param dict body_dict: The body of the item to be created.
        """
        response = self.itemsapi.post_item_with_http_info( # type: ignore
            body={
                "category_id": category,
            }
        ) 
        locationHeaderInResponse: str = str(response[2].get("Location")) #type: ignore
        print(f"The newly created item is here: {locationHeaderInResponse}")
        item_id:int = int(locationHeaderInResponse.split("/").pop())
        self.change_item(item_id, body_dict)

    def change_item(self, id: int, body_dict: dict[str, Any]) -> None:
        """
        Changes the item with the given ID to the given body_dict.
            :param int id: The ID of the item to be changed.
            :param dict body_dict: The body of the item to be changed.
        """
        self.itemsapi.patch_item(id, body=body_dict) #type: ignore

    def upload_file(
        self, id:int, path:str, comment:str="", resource_type:str="items"
    ):  
        """
        Uploads a file to the ELN with the given ID and path.
            :param int id: The ID of the item to be uploaded to.
            :param str path: The path of the file to be uploaded.
            :param str comment: The comment to be added to the file.
            :param str resource_type: The type of resource to be uploaded to. Can be 'item' or 'experiment'.
        """
        self.uploadsapi.post_upload(resource_type, id, file=path, comment=comment) #type: ignore
    def experiment_item_link(self, experiment_id: int, item_id: int):
        """
        Links an item to an experiment in the ELN with the given experiment ID and item ID.
            :param int experiment_id: The ID of the experiment to be linked to.
            :param int item_id: The ID of the item to be linked to.
        """
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
        """
        Adds a tag to an item in the ELN with the given item ID and tag. Take care to use correct capitalization/whitespace
            :param int item_id: The ID of the item to be tagged.
            :param str tag: The tag to be added to the item."""
        url = config.URL + "/items/" + str(item_id) + "/tags/"
        requests.post(url, headers=self.header, json={"tag": tag})

    def delete_upload(
        self, id:int, upload_id:int, resource_type:str="items"
    ):  
        """Deletes an upload from the ELN with the given ID and upload ID.
            :param int id: The ID of the item to be deleted.
            :param int upload_id: The ID of the upload to be deleted.
            :param str resource_type: The type of resource to be deleted. Can be 'item' or 'experiment'."""
        self.uploadsapi.delete_upload(resource_type, id, upload_id) #type: ignore   
    def get_metadata(self, id:int) -> dict[str, Any]:
        """
        Gets ONLY the metadata of an item in the ELN with the given ID.
            :param int id: The ID of the item to be gotten.
            :return: A dictionary containing the "metadata" of the item.
            """
        return json.loads(self.get_item(id)["metadata"])
    
    def get_item(self, id:int) -> dict[str, Any]:
        """
        Gets an item in the ELN with the given ID as a dictionary.
            :param int id: The ID of the item to be gotten.
            :return: A dictionary containing the item information, with {title, id, category, metadata,rating,tags} and many more fields."""
        return self.itemsapi.get_item(id).to_dict() #type: ignore
        # this dictionary should contain:
        # title, id, category, metadata, rating
        # a lot of items are contained in the metadata field, which is a json string
        # this can be easily converted to/from a python dictionary in any method used to edit metadata
    def get_experiment(self, id:int) -> dict[str, Any]:
        """
        Gets an experiment in the ELN with the given ID as a dictionary.
            :param int id: The ID of the experiment to be gotten.
            :return: A dictionary containing the experiment information, with {title, id, category, metadata,rating,tags} and many more fields.
        """
        return self.expapi.get_experiment(id).to_dict()

    def get_items_types(self) -> list[dict[str,Any]]: 
        """
        Gets the item type templates as dictionaries from the ELN.
            :return: A list of dictionaries containing the item type templates.
        """
        # construct full API URL
        url = (
            config.URL
            + "/items_types"
        )
        return requests.get(url, headers=self.header).json()

    def get_items(self, size:int=15) -> list[object]:
        """
        Gets a list of items in the ELN as dictionaries.
            :param int size: The number of items to be gotten. Defaults to 15, setting it too high (~1000) causes it to default back to 15.
            :return: A list of dictionaries containing the items.
        """
        # returns the most recent 15 if a size is not specified
        #TODO: figure out the max number of items that can be returned
        # construct full API URL
        url = (
            config.URL
            + "/items?limit="
            + str(size)
        )
        return requests.get(url, headers=self.header).json()
    def get_experiments(self) -> list[object]:
        """
        Gets a list of experiments in the ELN as dictionaries.
            :return: A list of dictionaries containing the experiments.
        """
        return self.expapi.read_experiments() #type: ignore

    def get_uploaded_files(self, id:int, resource_type:str="items") -> list:
        """
        Gets a list of uploaded files in the ELN with the given ID.
            :param int id: The ID of the item to be gotten.
            :param str resource_type: The type of resource to be gotten. Can be 'item' or 'experiment'.
            :return: A list of file objects that can be written to a file.
        """
        return self.uploadsapi.read_uploads( #type: ignore
            resource_type, id
        )
    def is_item_busy(self, id:int) -> bool:
        """
        Checks if an item in the ELN with the given ID is being edited.
            :param int id: The ID of the item to be checked.
            :return: True if the item is busy, False otherwise.
        """
        return self.get_url('/items/' + str(id)).json()['exclusive_edit_mode'] != [] # return True if item is busy, False otherwise
    def get_items_df(self, size:int=15):
        """
        Gets a list of items in the ELN as a pandas DataFrame.
            :param int size: The number of items to be gotten. Defaults to 15. Max of 9999.
            :return: A pandas DataFrame containing the items.
        """
        assert size <= 9999, "Size must be less than or equal to 9999"
        assert size > 0, "Size must be greater than 0"

        # TODO: consider moving get_items_df() to a different file so pandas isn't a req for simpler stuff
        def json_loads(x): 
            """function to get dictionaries from json, accounting for elements that may be dictionaries already, json strings, or None """
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
        
        df: pd.DataFrame = pd.DataFrame(self.get_items(size))
        df['metadata'] = df['metadata'].apply(json_loads)
        metadata: pd.DataFrame = df['metadata'].apply(pd.Series)
        extra_fields_df: pd.DataFrame = metadata['extra_fields'].apply(flatten_extra_fields).apply(pd.Series)
        df = pd.concat([df.drop(columns='metadata'), metadata.drop(columns='extra_fields'), extra_fields_df], axis=1)
        return df