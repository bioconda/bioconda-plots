import copy
import os
import json

downloads = {}
plot_data = []
packages = []

for filename in os.listdir('bioconda-stats/package-downloads/anaconda.org/bioconda/'):
    if filename.endswith(".json"):
        with open(f"bioconda-stats/package-downloads/anaconda.org/bioconda/{filename}", "r") as file:
            data = json.load(file)
            downloads[filename[:-5]] = data["downloads_per_date"].pop()["total"]

max_downloads = max(downloads.values())
data = [0] * int((max_downloads/100))

for i in range(int(max_downloads/100)):
    if i == 0:
        count = 0
    else:
        count = data[i - 1]
    for package, download_count in sorted(downloads.items(), key=lambda item: item[1]):
        if download_count <= i*100:
            count += 1
            packages.append({"package": package, "downloads": i*100, "count": count})
            del downloads[package]
        else:
            data[i] = count
            break

for (i, d) in enumerate(data[1:], 1):
    plot_data.append({"pos": i*100, "count": d})

if not os.path.exists("plots"):
    os.makedirs("plots")

with open("src/cdf.vl.json", "r") as vl_specs:
        plot = json.load(vl_specs)
        for p in packages:
            package = p["package"]
            if not os.path.exists(f"plots/{package}"):
                os.makedirs(f"plots/{package}")
            plot["data"]["values"] = copy.deepcopy(plot_data)
            plot["data"]["values"].append(p)
            with open(f"plots/{package}/cdf.vl.json", "w") as cdf:
                cdf.writelines(json.dumps(plot))
