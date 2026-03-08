import os
import glob

def reassemble_file(dataset_name="New plant Diseases Dataset Detection.zip"):
    part_files = sorted(glob.glob(f"{dataset_name}.part*"))
    if not part_files:
        print("No part files found. Did you download them all?")
        return

    print(f"Found {len(part_files)} parts. Reassembling into {dataset_name}...")
    with open(dataset_name, 'wb') as outfile:
        for part in part_files:
            print(f"Adding {part}...")
            with open(part, 'rb') as infile:
                outfile.write(infile.read())
    print("Dataset reassembled successfully!")

if __name__ == '__main__':
    reassemble_file()
