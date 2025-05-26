import gdown

# Google Drive file ID for drugs dataset
file_id = "1iY22o27KKHMhF5b2Rih1N3AJipsjW59D"
output_file = "fars_drugs_2008_2023_combined.csv"

# Download the file
gdown.download(f"https://drive.google.com/uc?id={file_id}", output_file, quiet=False)

print("✅ File downloaded:", output_file)
