import csv
import eln_packages_common.resourcemanage

rm = eln_packages_common.resourcemanage.Resource_Manager()

target_columns = [
    # "id",
    "title",
    "CAS",

    "Quantity",
    "Quantity Units",
    "category",
    "Room",
    "Location",

    "State",
    "Opened",
    "Received",

    "Mn", 
    "Mw",
    "PDI",
    "SMILES",
    "BigSMILES",
    "Full name",

    "Lot number",
    # "Hazards Link",
    "Manufacturer", 
    # "Pubchem Link", 
    "Container type", 
    "Molecular Weight", 
    "Solvent",
    "Solvent CAS", 
    "Concentration", 
    "Solvent SMILES", 
    "Purity", 
    "Big SMILES",
    "Name",
    "Smile",
    "Big Smile"
]

df = rm.get_items_df(size=1000)
df = df[target_columns]
df.to_csv("2025-05-27_inventory.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
print("Inventory saved to 2025-05-27_inventory.csv")