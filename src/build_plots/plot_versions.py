import io
import os
import pandas as pd
import sys
from git import Repo
from logging import INFO, basicConfig, getLogger
from .common import buildDailyPlot


basicConfig(level=INFO)
logger = getLogger(__name__)

days_to_plot = 15
if len(sys.argv) > 1 and sys.argv[1]:
    # Add 1 to get the delta for the last date
    days_to_plot = int(sys.argv[1]) + 1

max_packages = None
if len(sys.argv) > 2 and sys.argv[2]:
    max_packages = int(sys.argv[2])

buildDailyPlot("versions", "subdir", max_packages, days_to_plot)