import io
import os
import pandas as pd
from git import Repo
from logging import INFO, basicConfig, getLogger
from ._vendor.conda.models.version import VersionOrder


basicConfig(level=INFO)
logger = getLogger(__name__)


def buildDailyPlot(category, field, max_packages, days_to_plot):
    if not os.path.exists("plots"):
        os.makedirs("plots")

    repo = Repo("bioconda-stats")
    tags = repo.tags

    # for each package, get the most recent versions.tsv
    package_count = 0
    error_count = 0
    for filename in os.listdir(
        f"bioconda-stats/package-downloads/anaconda.org/bioconda/{category}"
    ):
        if filename.endswith(".tsv"):
            package = filename[:-4]
            try:
                logger.debug(f"Loading data for package: {package}")
                package_df = pd.DataFrame()
                tagref = None

                df = pd.read_csv(
                    f"bioconda-stats/package-downloads/anaconda.org/bioconda/{category}/{filename}",
                    dtype={ field: str, "total": int },
                    encoding="utf-8",
                    sep="\t",
                )
                versions = set(df[field])
                prev_tagname = tags[len(tags) - 1].name

                # Get tags going back 15 days (or as specified in arg)
                for days_back in range(1, days_to_plot):
                    if tagref is not None:
                        prev_tagname = tagref.name
                    tagref = tags[len(tags) - 1 - days_back]

                    # Get a previous tagged version of the package stats tsv
                    try:
                        subtree = (
                            tagref.commit.tree
                            / f"package-downloads/anaconda.org/bioconda/{category}"
                        )
                        blob = subtree / filename
                    except KeyError:
                        # does not exist
                        break

                    logger.debug(f"Found data for {package} from date {tagref.name}.")
                    new_df = pd.read_csv(
                        io.BytesIO(blob.data_stream.read()),
                        dtype={ field: str, "total": int },
                        encoding="utf-8",
                        sep="\t"
                    )
                    # do a delta between totals of different dates
                    versions = versions | set(new_df[field])
                    df_sub = df.set_index(field).subtract(
                        new_df.set_index(field), fill_value=0
                    )
                    df_sub.rename(columns={"total": "delta"}, inplace=True)
                    df = df.merge(df_sub, on=field)
                    df["date"] = prev_tagname
                    package_df = pd.concat([package_df, df], ignore_index=True)
                    df = new_df

                if len(package_df.index) > 0:
                    version_list = list(versions)
                    # Get 7 most recent versions, sorting by VersionOrder
                    if category == "versions":
                        version_list = sorted(version_list, key=VersionOrder)[-7:]
                    package_df[field] = pd.Categorical(
                        package_df[field], ordered=True, categories=version_list
                    )
                    package_df = package_df[package_df[field].notna()].sort_values(
                        by=[field, "date"]
                    )[["date", "total", "delta", field]]

                    # Save plot data
                    if not os.path.exists(f"plots/{package}"):
                        os.makedirs(f"plots/{package}")
                    with open(f"plots/{package}/{category}.json", "w") as v:
                        v.writelines(package_df.to_json(orient="records"))
                        logger.debug(f"Saved data for {package} to {category}.json.")

            except Exception as e:
                # Log package name and continue with the rest
                error_count += 1
                e.args = (f"Error creating plot for {package}.",) + e.args
                logger.exception(e)

            finally:
                package_count += 1
                if max_packages and package_count == max_packages:
                    break

    if error_count > 0:
        raise RuntimeError(
            f"Errors occurred for {error_count} out of {package_count} packages."
        )
    else:
        logger.info(f"Completed {package_count} packages.")
