import pandas as pd
from pathlib import Path
import sys
import os

def convert_excel_to_csv(excel_file: str, output_dir: str = None) -> str:
    """
    Convert an Excel file to CSV format
    
    Args:
        excel_file (str): Path to the Excel file
        output_dir (str, optional): Directory to save the CSV file. If None, uses same directory as Excel file
        
    Returns:
        str: Path to the created CSV file
    """
    try:
        # Get the absolute path of the Excel file
        excel_path = Path(excel_file).resolve()
        
        # If output directory is not specified, use the same directory as the Excel file
        if output_dir is None:
            output_dir = excel_path.parent
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output CSV filename
        csv_filename = excel_path.stem + '.csv'
        csv_path = output_dir / csv_filename
        
        # Read Excel file
        print(f"Reading Excel file: {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Clean column names
        df.columns = [col.strip().title() for col in df.columns]
        
        # Remove any empty rows
        df = df.dropna(how='all')
        
        # Save to CSV
        print(f"Saving CSV file: {csv_path}")
        df.to_csv(csv_path, index=False)
        
        print(f"Successfully converted {excel_path} to {csv_path}")
        return str(csv_path)
        
    except Exception as e:
        print(f"Error converting {excel_file} to CSV: {str(e)}")
        return None

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    # List of Excel files to convert
    excel_files = [
        "mi_players.xlsx",
        "csk_players.xlsx"
    ]
    
    print("Starting Excel to CSV conversion...")
    
    # Convert each Excel file
    for excel_file in excel_files:
        excel_path = data_dir / excel_file
        if excel_path.exists():
            csv_path = convert_excel_to_csv(str(excel_path))
            if csv_path:
                print(f"✓ Successfully converted {excel_file}")
            else:
                print(f"✗ Failed to convert {excel_file}")
        else:
            print(f"✗ Excel file not found: {excel_file}")
    
    print("\nConversion process completed!")

if __name__ == "__main__":
    main() 