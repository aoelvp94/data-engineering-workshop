"""
Module containing constants for Airflow DAGs.
"""
from pathlib import Path

from pkg_resources import resource_filename

PACKAGE_PATH = Path(resource_filename("de_workshop", "/"))

REPO_ROOT = PACKAGE_PATH.parent
DBT_PROJECT_DIR = REPO_ROOT / "dbt_project"
