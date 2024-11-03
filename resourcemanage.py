# right now i intend to create a class with a few methods to control
# resources (add/delete/edit) here, if this gets too complicated i may decide to
# split it into seperate files

# this contains mostly code written by Connor found in Python_Scripts.zip in the Onedrive.
# i am mostly writing wrappers and making the code a little more abstract and generally usable

from eln_packages_common import config
import json
import requests


class Resource_Manager:
    def __init__(self):
        self.itemsapi = config.load_items_api()
        self.expapi = config.load_experiments_api()
        self.uploadsapi = config.load_uploads_api()
        self.printer_path = config.PRINTER_PATH  # this is the path where the labels will be saved, it is set in the config file, and accessed in printer/generate_label.py

    def create_item(self, category: int, body_dict: dict):
        response = self.itemsapi.post_item_with_http_info(
            body={
                "category_id": category,
            }
        )
        locationHeaderInResponse = response[2].get("Location")
        print(f"The newly created item is here: {locationHeaderInResponse}")
        item_id = int(locationHeaderInResponse.split("/").pop())
        self.change_item(item_id, body_dict)

    def change_item(self, id: int, body_dict: dict):
        self.itemsapi.patch_item(id, body=body_dict)
    def get_metadata(self, id) -> dict:
        return json.loads(self.get_item(id)["metadata"])
    def get_item(self, id) -> dict:
        return self.itemsapi.get_item(id).to_dict()
        # this dictionary should contain:
        # title, id, category, metadata, rating
        # a lot of items are contained in the metadata field, which is a json string
        # this can be easily converted to/from a python dictionary in any method used to edit metadata

    def experiment_item_link(self, experiment_id: int, item_id: int):
        ## copied heavily from Connor's code, there may be a way to do this with the elabftw API
        ## but there isn't a documented way, and it was easier to just use the requests library.

        # get basic config information
        header = config.api_client.default_headers
        header = {**header, **{"Content-type": "application/json"}}
        # construct full API URL
        url = (
            config.URL
            + "/experiments/"
            + str(experiment_id)
            + "/items_links/"
            + str(item_id)
        )
        # send the request
        requests.post(url, headers=header)
    
    def get_items_types(self) -> list[dict]:
        header = config.api_client.default_headers
        header = {**header, **{"Content-type": "application/json"}}
        # construct full API URL
        url = (
            config.URL
            + "/items_types"
        )
        return requests.get(url, headers=header).json()

    def add_tag(self, item_id: int, tag: str):
        header = config.api_client.default_headers
        header = {**header, **{"Content-type": "application/json"}}
        url = config.URL + "/items/" + str(item_id) + "/tags/"
        requests.post(url, headers=header, json={"tag": tag})

    def get_items(self, size=None) -> list[config.elabapi_python.models.item.Item]:
    # returns the most recent 15 if a size is not specified
        return self.itemsapi.read_items(limit=size)

    def get_experiments(self) -> list[config.elabapi_python.models.experiment.Experiment]:
        return self.expapi.read_experiments()

    def upload_file(
        self, id, path, comment="", resource_type="items"
    ):  # resource_type can be 'item' or 'experiment', wraps the upload api
        self.uploadsapi.post_upload(resource_type, id, file=path, comment=comment)

    def delete_upload(
        self, id, upload_id, resource_type="items"
    ):  # resource_type can be 'item' or 'experiment', wraps the upload api
        self.uploadsapi.delete_upload(resource_type, id, upload_id)

    def get_uploaded_files(self, id, resource_type="items") -> list[config.elabapi_python.models.upload.Upload]:
        return self.uploadsapi.read_uploads(
            resource_type, id
        )  # returns a list of file objects that can be written to a file
