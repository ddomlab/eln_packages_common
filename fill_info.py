import pubchempy as pcp
import json
from eln_packages_common.resourcemanage import Resource_Manager

rm = Resource_Manager()
# CAS numbers fall in the 'name' category on pubchem, so they are searched as names
# you could also search by the common name or any other synonym, however CAS numbers
# should return more consistent results
def get_compound(CAS) -> pcp.Compound:
    compound_list: list[pcp.Compound] = pcp.get_compounds(CAS, "name")
    if len(compound_list) > 1:
        raise ValueError(
            "Multiple compounds with this name have been found, please input a more specific name or CAS number"
        )
    elif len(compound_list) == 0:
        raise ValueError("No compound with this name has been found")
    compound: pcp.Compound = compound_list[0]
    return compound


def check_if_cas(input: str) -> bool:
    for char in input:
        if not char.isdigit() and char != "-":
            return False
    return True


def fill_in(id: int):
    body: dict = rm.get_item(id)
    metadata: dict = json.loads(body["metadata"])
    new_title: str = body["title"]
    if check_if_cas(body["title"]): 
        # if the title is a CAS number, search by CAS number, and replace the title with the first synonym on PubChem
        CAS: str = body["title"]
        compound: pcp.Compound = get_compound(body["title"])
        new_title = compound.synonyms[0]
        print(compound.synonyms[0])
    elif "CAS" in metadata["extra_fields"]:
        # if the title is not a CAS but there is a CAS in the metadata, search by that CAS
        CAS = metadata["extra_fields"]["CAS"]["value"]
        compound: pcp.Compound = get_compound(CAS)
    else:
        # otherwise try to search by the non-CAS title
        compound: pcp.Compound = get_compound(body["title"])
    metadata["extra_fields"]["Full name"]["value"] = compound.iupac_name

    if "SMILES" not in metadata["extra_fields"]:
        # if there isn't a SMILES field, create one
        metadata["extra_fields"]["SMILES"] = {
            "type": "text",
            "value": "",
            "description": "From PubChem",
        }
    metadata["extra_fields"]["SMILES"]["value"] = compound.isomeric_smiles
    if "CAS" not in metadata["extra_fields"]:
        # if there isn't a CAS field, create one
        metadata["extra_fields"]["CAS"] = {
            "type": "text",
            "value": "",
            "description": "",
        }
    metadata["extra_fields"]["CAS"]["value"] = CAS
    if "Molecular Weight" not in metadata["extra_fields"]:
        # if there isn't a molecular weight field, create one #TODO: make this a number
        metadata["extra_fields"]["Molecular Weight"] = {
            "type": "text",
            "value": "",
            "description": "From PubChem (g/mol)",
        }
    metadata["extra_fields"]["Molecular Weight"]["value"] = compound.molecular_weight
    if "Pubchem Link" not in metadata["extra_fields"]:
        # if there isn't a Pubchem link field, create one
        metadata["extra_fields"]["Pubchem Link"] = {
            "type": "url",
            "value": "",
            "description": "Link to PubChem page",
        }
    metadata["extra_fields"]["Pubchem Link"]["value"] = (
        f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid}"
    )
    if "Hazards Link" not in metadata["extra_fields"]:
        # if there isn't a hazards link field, create one
        metadata["extra_fields"]["Hazards Link"] = {
            "type": "url",
            "value": "",
            "description": "Link to Hazards section of PubChem",
        }
    metadata["extra_fields"]["Hazards Link"]["value"] = (
        f"https://pubchem.ncbi.nlm.nih.gov/compound/{compound.cid}#section=Hazards-Identification"
    )
    new_body = {
        "title": new_title,
        "metadata": json.dumps(metadata),
        "rating": 0, # before i figured out tags I used this to mark autofilled items, no longer necessary. this will remove ratings
    }
    rm.change_item(id, new_body)
