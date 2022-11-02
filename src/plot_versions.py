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

        if all([all(list(map(lambda x: x.isdigit(), v.split('.')))) for v in versions]):
            versions.sort(key=lambda s: list(map(int, s.split('.'))))

        for version in versions[-7:]:
            with open(f"bioconda-stats/package-downloads/anaconda.org/bioconda/{package}/{version}.json", "r") as file:
                data = json.load(file)
                data = data["downloads_per_date"]
                days = min(len(data), 15)
                data = data[-days:]
                for i, entry in enumerate(data[-(days - 1):], 1):
                    entry["delta"] = entry["total"] - data[i - 1]["total"]
                    entry["version"] = version
                values.extend(data[-(days - 1):])

            with open(f"plots/{package}/versions.json", "w") as v:
                v.writelines(json.dumps(values))
