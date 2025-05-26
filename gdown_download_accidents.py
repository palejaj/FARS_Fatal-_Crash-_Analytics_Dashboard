import gdown

# Google Drive file ID
file_id = "1KjeqZrNVGniToUYrW9uQOWckeVFEmRCy"
output_file = "fars_accidents_1975_2023_cleaned.csv"

# Download the file
gdown.download(f"https://drive.google.com/uc?id={file_id}", output_file, quiet=False)

print("✅ File downloaded:", output_file)
