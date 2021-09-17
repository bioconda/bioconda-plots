import os
import json
import sys

downloads = {}
plot_data = []

for filename in os.listdir('bioconda-stats/package-downloads/anaconda.org/bioconda/'):
    if filename.endswith(".json"):
        with open(f"bioconda-stats/package-downloads/anaconda.org/bioconda/{filename}", "r") as file:
            data = json.load(file)
            downloads[filename.strip(".json")] = data["downloads_per_date"].pop()["total"]

for i, (package, download_count) in enumerate(sorted(downloads.items(), key=lambda item: item[1])):
    if i == 0:
        plot_data.append({"pos": i, "count": download_count})
    else:
        plot_data.append({"pos": i, "count": plot_data[i - 1]["count"] + download_count})

with open("src/plot.vl.json", "r") as vl_specs:
    plot = json.load(vl_specs)
    plot["data"]["values"] = plot_data
    sys.stdout.write(json.dumps(plot))