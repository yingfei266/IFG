"""Creates functional group excel data sheet given a target smiles code set from a text file"""

import csv
import logging
import os
import traceback

import pandas
from tqdm import tqdm

from chem.molecule import Molecule

##### Target Molecular SMILES Codes #####
STRUCTURES_PATH = os.path.dirname(__file__) + "/smiles/smiles.csv"
"""Hydrogen-suppressed organic molecule SMILES codes file to process in this script"""

##### Target Main Output Excel Sheet #####
MAIN_OUTPUT_PATH = os.path.dirname(__file__) + '/output/functional_groups.xlsx'
"""Excel file generated by this script"""

##### Failed Structure Logging Setup #####
with open("main.log", mode="w", encoding="UTF-8") as file:
    file.truncate(0)
logging.basicConfig(format='%(message)s', filename='main.log')

##### Data Variables #####
all_data: list[dict] = []
exact_data: list[dict] = []
mol: Molecule
failed_mols: list[str] = []

##### Input Structure Data Load #####
STRUCTURES_CSV_FILE = csv.reader(open(STRUCTURES_PATH, "r+", encoding="UTF-8"))
STRUCTURES = [(smiles,refcode) for (smiles,refcode) in STRUCTURES_CSV_FILE][1:]

##### Structure Bar Status #####
with tqdm(total=len(STRUCTURES)) as bar:

    ##### SMILES Structure Loop #####
    for (smiles, refcode) in STRUCTURES:

        ##### Molecule Data #####
        try:
            mol = Molecule(smiles, name=refcode, type='mol')
        except BaseException as exception:
            failed_mols.append(smiles + " " + refcode)
            print("  ", smiles, "Failed to be processed")
            logging.error(f"{refcode} {smiles} Failed to be processed \n {traceback.format_exc()}")
            continue

        ##### All Functional Group Format Data #####
        all_data.append({
            "Refcode": mol.name,
            "SMILES": smiles,
            "Aromatic Rings": mol.aromatic_ring_count,
            "Non Aromatic Rings": mol.non_aromatic_ring_count,
            "Rings": mol.total_ring_count,
            "AminoAcid": "Yes" if mol.amino_acid else "No",
            **mol.functional_groups_all,
        })

        ##### Exact Functional Group Format Data #####
        exact_data.append({
            "Refcode": mol.name,
            "SMILES": smiles,
            "Aromatic Rings": mol.aromatic_ring_count,
            "Non Aromatic Rings": mol.non_aromatic_ring_count,
            "Rings": mol.total_ring_count,
            "AminoAcid": "Yes" if mol.amino_acid else "No",
            **mol.functional_groups_exact,
        })

        ##### Status Bar Update #####
        bar.update(1)                                               # Increment the progress bar once smiles finishes processing

##### Pandas Dataframe #####
df_all = pandas.DataFrame(all_data).fillna(0).set_index("Refcode")
df_exact = pandas.DataFrame(exact_data).fillna(0).set_index("Refcode")

##### Excel Exporter (xlsx file type) #####
writer = pandas.ExcelWriter(MAIN_OUTPUT_PATH)

##### All Functional Groups Data Sheet Export #####
df_all.to_excel(writer, sheet_name="all_data", freeze_panes=(1, 1))
all_sheet = writer.sheets["all_data"]
all_sheet.set_column(0, 0, 13)      # Refcode column width
all_sheet.set_column(1, 1, 125)     # SMILES column width
df_all_columns: list[str] = [str(col) for col in df_all.columns][1:]
for i, col in enumerate(df_all_columns):
    all_sheet.set_column(i+2, i+2, len(col)+7)

##### Exact Functional Groups Data Sheet Export #####
df_exact.to_excel(writer, sheet_name="exact_data", freeze_panes=(1, 1))
exact_sheet = writer.sheets["exact_data"]
exact_sheet.set_column(0, 0, 13)      # Refcode column width
exact_sheet.set_column(1, 1, 125)     # SMILES column width
df_exact_columns: list[str] = [str(col) for col in df_exact.columns][1:]
for i, col in enumerate(df_exact_columns):
    exact_sheet.set_column(i+2, i+2, len(col)+7)

##### Excel File Save #####
writer.close()

##### Structure Error Result Logging #####
if failed_mols:
    logging.error("##### Failed SMILES codes #####")
else:
    logging.error("Last execution was successfull for all structures")
for failed_mol in failed_mols:
    logging.error(failed_mol)