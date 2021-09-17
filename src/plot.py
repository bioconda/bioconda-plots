import os
import json

downloads = {}

for filename in os.listdir('bioconda-stats/package-downloads/anaconda.org/bioconda/'):
    if filename.endswith(".json"):
        with open(f"bioconda-stats/package-downloads/anaconda.org/bioconda/{filename}", "r") as file:
            data = json.load(file)
            downloads[filename.strip(".json")] = data["downloads_per_date"].pop()["total"]

print(downloads)