import os

def split_file(filepath, chunk_size_mb=50):
    chunk_size = chunk_size_mb * 1024 * 1024
    part_num = 1
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            part_name = f"{filepath}.part{part_num:03d}"
            with open(part_name, 'wb') as part_file:
                part_file.write(chunk)
            print(f"Created {part_name}")
            part_num += 1

if __name__ == '__main__':
    dataset_file = 'New plant Diseases Dataset Detection.zip'
    if os.path.exists(dataset_file):
        print(f"Splitting {dataset_file}...")
        split_file(dataset_file)
        print("Done splitting!")
    else:
        print("File not found.")
