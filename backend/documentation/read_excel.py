import pandas as pd
import sys

def analyze_excel(file_path):
    try:
        # Load the excel file
        xl = pd.ExcelFile(file_path)
        print(f"Sheet Names: {xl.sheet_names}\n")
        
        # Print a preview of each sheet
        for sheet in xl.sheet_names:
            print(f"--- Sheet: {sheet} ---")
            df = xl.parse(sheet, nrows=10) # Print first 10 rows
            print(df.to_string())
            print("\n")
            
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    file_path = r"d:\CODES\OBE\backend\OBE calculations try 2_11072025 (1).xlsx"
    analyze_excel(file_path)
