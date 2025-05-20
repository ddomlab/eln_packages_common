import pandas as pd
import eln_packages_common.resourcemanage
from eln_packages_common.fill_info import check_if_cas


rm = eln_packages_common.resourcemanage.Resource_Manager()
df = rm.get_items_df(size=1000)
items = df[["id", "CAS"]]
df = rm.get_compounds_df()
comps = df[["id", "cas_number"]]

for _, item_row in items.iterrows():
    cas = str(item_row["CAS"]).strip()
    resource_id = item_row["id"]

    if check_if_cas(cas):
        # Find matching compound row(s) by CAS
        matching_comps = comps[comps["cas_number"].astype(str).str.strip() == cas]
        print(f"Found {len(matching_comps)} matching compounds for CAS: {cas} and resource ID: {resource_id}")
        for _, comp_row in matching_comps.iterrows():
            compound_id = comp_row["id"]
            rm.associate_compound(compound_id, resource_id)
    # else: 
        # print(f"Invalid CAS number: {cas} for resource ID: {resource_id}")