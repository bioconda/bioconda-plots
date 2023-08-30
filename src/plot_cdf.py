import json
import os
import pandas as pd

plot_data = []
packages = []

# Get most recent number of downloads for each package
df = pd.read_csv("bioconda-stats/package-downloads/anaconda.org/bioconda/packages.tsv", sep="\t")
downloads = df.sort_values(by=['total'])
downloads = downloads.set_index("package")
downloads = downloads.to_dict('dict')

# init array with number of items equal to highest number of downloads of any given package divided by 100
max_downloads = df["total"].max()
data = [0] * int((max_downloads/100))

# For each of these buckets, count and collect the packages with downloads <= to the bucket range (1/100th of the max downloads)
for i in range(int(max_downloads/100)):
    if i == 0:
        count = 0
    else:
        count = data[i - 1]
    package_list = list(downloads["total"].items())
    for package, download_count in package_list:
        if download_count <= i*100:
            count += 1
            packages.append({"package": package, "downloads": i*100, "count": count})
            del downloads["total"][package]
        else:
            data[i] = count
            break


# The overall plot has the number of packages in each download count bucket
for (i, d) in enumerate(data[1:], 1):
    plot_data.append({"pos": i*100, "count": d})

if not os.path.exists("plots"):
    os.makedirs("plots")

with open(f"plots/cdf.json", "w") as cdf:
    cdf.writelines(json.dumps(plot_data))

# The per item cdf.json contains the x,y point for this particular package.
for p in packages:
    package = p["package"]
    if not os.path.exists(f"plots/{package}"):
        os.makedirs(f"plots/{package}")
    with open(f"plots/{package}/cdf.json", "w") as cdf:
        cdf.writelines(json.dumps([p]))
