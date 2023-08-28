import io
import os
import pandas as pd
from git import Repo
from logging import INFO, basicConfig, getLogger


basicConfig(level=INFO)
logger = getLogger(__name__)

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
        try:
            logger.debug(f"Loading data for package: {package}")
            package_df = pd.DataFrame()
            tagref = None

            df = pd.read_csv(f"bioconda-stats/package-downloads/anaconda.org/bioconda/versions/{filename}", encoding="utf-8", sep="\t")
            versions = set(df["version"])
            prev_tagname = tags[len(tags) - 1].name

            # Get tags going back 15 days
            for days_back in range(1, 15):
                if tagref is not None:
                    prev_tagname = tagref.name
                tagref = tags[len(tags) - 1 - days_back]
                subtree = (
                    tagref.commit.tree / "package-downloads/anaconda.org/bioconda/versions"
                )

                # Get a previous tagged version of the package stats tsv
                try:
                    blob = subtree / filename
                except KeyError:
                    # does not exist
                    break

                logger.debug(f"Found data for {package} from date {tagref.name}.")
                new_df = pd.read_csv(
                    io.BytesIO(blob.data_stream.read()), encoding="utf-8", sep="\t"
                )
                # do a delta between totals of different dates
                versions = versions | set(new_df["version"])
                df_sub = df.set_index("version").subtract(new_df.set_index("version"), fill_value=0)
                df_sub.rename(columns={"total": "delta"}, inplace=True)
                df = df.merge(df_sub, on="version")
                df["date"] = prev_tagname
                package_df = pd.concat([package_df, df], ignore_index=True)
                df = new_df

            if len(package_df.index) > 0:
                # Sort by version (for semantic versioning)
                versions = list(versions)
                if all([all(list(map(lambda x: x.isdigit(), str(v).split(".")))) for v in versions]):
                    versions.sort(key=lambda s: list(map(int, str(s).split("."))))
                
                package_df["version"] = pd.Categorical(package_df["version"], ordered=True, categories=versions)
                package_df = package_df.sort_values(by=["version","date"])[["date", "total", "delta", "version"]]

                # Save plot data
                if not os.path.exists(f"plots/{package}"):
                    os.makedirs(f"plots/{package}")
                with open(f"plots/{package}/versions.json", "w") as v:
                    v.writelines(package_df.to_json(orient="records"))
                    logger.debug(f"Saved data for {package} to versions.json.")

        except Exception as e:
            # Log package name and continue with the rest
            e.args = (f"Error creating plot for {package}.",) + e.args
            logger.exception(e)

