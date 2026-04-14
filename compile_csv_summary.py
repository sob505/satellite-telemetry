import csv
import os
from pathlib import Path


def compile_csv_summary(data_dir='data', output_file='summary.csv'):
    """
    Read all CSV files from a directory and compile a summary CSV file.
    
    The output CSV contains:
    - filename: The name of the original CSV file
    - header: The first line (header) of the CSV file
    - example_row: The first data row of the CSV file
    
    Args:
        data_dir (str): Path to the directory containing CSV files. Default is 'data'.
        output_file (str): Path to the output CSV file. Default is 'csv_summary.csv'.
    
    Returns:
        int: Number of CSV files processed.
    """
    
    # Ensure the data directory exists
    if not os.path.isdir(data_dir):
        print(f"Error: Directory '{data_dir}' does not exist.")
        return 0
    
    # Get all CSV files in the directory
    csv_files = sorted(Path(data_dir).glob('*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in '{data_dir}'.")
        return 0
    
    # Prepare data for output
    summary_data = []
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                
                # Read first two lines
                header = next(reader, None)
                example_row = next(reader, None)
                
                if header is not None:
                    # Convert lists to strings (joining with comma for readability)
                    header_str = ','.join(header) if header else ''
                    example_str = ','.join(example_row) if example_row else ''
                    
                    summary_data.append({
                        'filename': csv_file,
                        'header': header_str,
                        'example_row': example_str
                    })
        
        except Exception as e:
            print(f"Error reading {csv_file.name}: {e}")
            continue
    
    # Write summary to output CSV file
    if summary_data:
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['filename', 'header', 'example_row'])
                writer.writeheader()
                writer.writerows(summary_data)
            
            print(f"Summary CSV created: {output_file}")
            print(f"Processed {len(summary_data)} CSV files.")
            return len(summary_data)
        
        except Exception as e:
            print(f"Error writing output file: {e}")
            return 0
    else:
        print("No valid CSV files were processed.")
        return 0


if __name__ == '__main__':
    # Run with default parameters
    compile_csv_summary()
