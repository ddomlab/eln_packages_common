import pandas as pd
import eln_packages_common.resourcemanage

rm = eln_packages_common.resourcemanage.Resource_Manager()

target_columns = [
    "id","title", "category", "Mn", "Mw", "CAS", "PDI", "Room", "State", "Opened", "SMILES", "Location",
    "Quantity", "Received", "BigSMILES", "Full name", "Lot number", "Hazards Link",
    "Manufacturer", "Pubchem Link", "Container type", "Molecular Weight", "Solvent",
    "Solvent CAS", "Concentration", "Solvent SMILES", "Purity", "Big SMILES",
    "Name", "Smile", "Big Smile"
]

df = rm.get_items_df(size=1000)
df = df[target_columns]
print(df["id"])