import os
import json
import sys
import argparse

parser = argparse.ArgumentParser(description='Package to be plotted.')
parser.add_argument('package', type=str,
                    help='Package to be plotted over cdf of all packages')

args = parser.parse_args()

to_be_plotted = args.package

downloads = {}
plot_data = []

for filename in os.listdir('bioconda-stats/package-downloads/anaconda.org/bioconda/'):
    if filename.endswith(".json"):
        with open(f"bioconda-stats/package-downloads/anaconda.org/bioconda/{filename}", "r") as file:
            data = json.load(file)
            downloads[filename.strip(".json")] = data["downloads_per_date"].pop()["total"]

max_downloads = max(downloads.values())
data = [0] * max_downloads

for i in range(max_downloads):
    if i == 0:
        count = 0
    else:
        count = data[i - 1]
    for package, download_count in sorted(downloads.items(), key=lambda item: item[1]):
        if download_count <= i:
            count += 1
            del downloads[package]
        else:
            data[i] = count
            break

for (i, d) in enumerate(data):
    plot_data.append({"pos": i, "count": d})


with open("src/plot.vl.json", "r") as vl_specs:
    plot = json.load(vl_specs)
    plot["data"]["values"] = plot_data
    sys.stdout.write(json.dumps(plot, indent=4))