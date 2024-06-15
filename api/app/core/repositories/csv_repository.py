import csv
from pathlib import Path

class CsvRepository:
    def __init__(self, file_path):
        self.file_path = file_path
        self.create_file_if_not_exists()

    def create_file_if_not_exists(self):
        path = Path(self.file_path)
        if not path.exists():
            path.touch()

    def save_data(self, data):
        with open(self.file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            if isinstance(data, dict):
                # Write dictionary keys as headers if file is empty
                file.seek(0, 2)  # Move to the end of the file
                if file.tell() == 0:
                    writer.writerow(data.keys())
                writer.writerow(data.values())
            elif isinstance(data, list):
                if all(isinstance(item, dict) for item in data):
                    # Write dictionary keys as headers if file is empty
                    file.seek(0, 2)  # Move to the end of the file
                    if file.tell() == 0:
                        writer.writerow(data[0].keys())
                    writer.writerows(item.values() for item in data)
                else:
                    writer.writerows(data)
            else:
                writer.writerow(data)
    
    def get_data(self, filters=None, projection=None):
        result = []
        with open(self.file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if filters is None or all(row.get(key) == value for key, value in filters.items()):
                    if projection is None:
                        result.append(row)
                    else:
                        projected_row = {key: row.get(key) for key in projection}
                        result.append(projected_row)
        return result
    
    def get_all_data(self):
        return self.get_data()