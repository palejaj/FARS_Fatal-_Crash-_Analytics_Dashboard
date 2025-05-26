import gdown

# Google Drive file ID for person dataset
file_id = "1LRnoGp_CMhRNwq9QhUlgA8h7qfR6dja1"
output_file = "fars_person_2008_2023_combined.csv"

# Download the file
gdown.download(f"https://drive.google.com/uc?id={file_id}", output_file, quiet=False)

print("✅ File downloaded:", output_file)
