import io
import os
import pandas as pd
from git import Repo

if not os.path.exists("plots"):
    os.makedirs("plots")

repo = Repo("bioconda-stats")
tags = repo.tags

# for each package, get the most recent versions.tsv
for filename in os.listdir(
    "bioconda-stats/package-downloads/anaconda.org/bioconda/versions"
):
    if filename.endswith(".tsv"):
        package = filename[:-4]

        if not os.path.exists(f"plots/{package}"):
            os.makedirs(f"plots/{package}")

        versions = set()
        package_df = pd.DataFrame()
        df = None
        tagref = None
        prev_tag = None
        # Get tags going back 15 days
        for days_back in range(0, 15):
            if tagref is not None:
                prev_tag = tagref
            tagref = repo.tags[len(repo.tags) - 1 - days_back]
            subtree = (
                tagref.commit.tree / "package-downloads/anaconda.org/bioconda/versions"
            )

            # Get a previous tagged version of the package stats tsv
            try:
                blob = subtree / filename
            except KeyError:
                # does not exist
                continue

            new_df = pd.read_csv(
                io.BytesIO(blob.data_stream.read()), encoding="utf-8", sep="\t"
            )
            # do a delta between totals of different dates
            versions = versions | set(new_df["version"])
            if df is not None:
                df_sub = df.set_index("version").subtract(new_df.set_index("version"), fill_value=0)
                df_sub.rename(columns={"total": "delta"}, inplace=True)
                df = df.merge(df_sub, on="version")
                df["date"] = prev_tag.name
                package_df = pd.concat([package_df, df], ignore_index=True)
            df = new_df

        # Sort by version (for semantic versioning)
        versions = list(versions)
        if all([all(list(map(lambda x: x.isdigit(), str(v).split('.')))) for v in versions]):
            versions.sort(key=lambda s: list(map(int, str(s).split('.'))))
        
        package_df['version'] = pd.Categorical(package_df['version'], ordered=True, categories=versions)
        package_df = package_df.sort_values(by=['version','date'])[["date", "total", "delta", "version"]]

        # Save plot data
        with open(f"plots/{package}/versions.json", "w") as v:
            v.writelines(package_df.to_json(orient='records'))
