import json
import os

if not os.path.exists("plots"):
    os.makedirs("plots")

for filename in os.listdir('bioconda-stats/package-downloads/anaconda.org/bioconda/'):
    if filename.endswith(".json"):
        package = filename[:-5]

        if not os.path.exists(f"plots/{package}"):
            os.makedirs(f"plots/{package}")

        versions = []
        values = []
        for version_filename in os.listdir(f'bioconda-stats/package-downloads/anaconda.org/bioconda/{package}'):
            if version_filename.endswith(".json"):
                versions.append(version_filename[:-5])

        for version in versions:
            with open(f"bioconda-stats/package-downloads/anaconda.org/bioconda/{package}/{version}.json", "r") as file:
                data = json.load(file)
                data = data["downloads_per_date"][-15:]
                for i, entry in enumerate(data[-14:], 1):
                    entry["delta"] = entry["total"] - data[i - 1]["total"]
                    entry["version"] = version
                values.extend(data[-14:])

        with open("src/versions.vl.json", "r") as vl_specs:
            plot = json.load(vl_specs)
            plot["data"]["values"] = values
            with open(f"plots/{package}/versions.vl.json", "w") as v:
                v.writelines(json.dumps(plot))