import pandas as pd
import eln_packages_common.resourcemanage
from eln_packages_common.fill_info import check_if_cas

rm = eln_packages_common.resourcemanage.Resource_Manager()

df = rm.get_items_df(size=1000)
df = df["CAS"]
for d in df:
    if check_if_cas(str(d)):
        print(d)
        rm.find_and_create_compound(CAS=str(d))