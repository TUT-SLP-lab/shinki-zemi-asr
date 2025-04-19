import csv
import os

from src.shinki_zemi_asr.config import DATA_FILE


def initialize_data_file() -> None:
    """Create the data file with headers if it doesn't exist"""
    if not (os.path.exists(DATA_FILE)):
        with open(DATA_FILE, "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["presenter_name",
                             "date",
                             "start_time",
                             "end_time",
                             "file_path",
                             "is_processed",
                             "is_uploaded",
                             "is_deleted"
                            ])

def read_data_file() -> list[list[str]]:
    """Read all data from csv and return it as list"""
    result = []

    with open(DATA_FILE, "r", newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader, None)
        for row in csv_reader:
            result.append(row)
    return result

def add_recording_data(presenter_name : str,
                       date : str,
                       start_time : str,
                       end_time : str,
                       file_path :str
                       ):
    """Add new recording to data file"""
    with open(DATA_FILE, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            presenter_name, 
            date, 
            start_time, 
            end_time, 
            file_path, 
            False, 
            False, 
            False
        ])

def update_processing_status(file_path: str, is_processed: bool = True):
    """Update the processing status for a specific recording."""
    # Read the current data
    rows = []
    with open(DATA_FILE, "r", newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        header = next(csv_reader)
        rows.append(header)
        
        for row in csv_reader:
            if row[4] == file_path:  # Check if file_path matches
                row[5] = str(is_processed)  # Update is_processed status
            rows.append(row)
    
    # Write the updated data back to the file
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(rows)

