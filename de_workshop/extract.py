"""Extract module for extractions"""
import logging

import pandas as pd

from de_workshop.config import PACKAGE_PATH
from de_workshop.constants import IGNORED_COLUMNS, TOPICS_OF_INTEREST
from de_workshop.helpers import GNews_wo_import, upload_to_minio


def get_data_from_gnews(topic: str, dry_run: bool = True) -> pd.DataFrame:
    """Get data from GNews according to a certain topic.

    Parameters
    ----------
    topic : str
        Topic of interest.

    Returns
    -------
    gnews_df : pd.DataFrame
        DF with GNews data.
    """
    if dry_run:
        cols = list(pd.read_csv(PACKAGE_PATH / "data.csv", nrows=1))
        gnews_df = pd.read_csv(
            PACKAGE_PATH / "data.csv",
            usecols=[c for c in cols if c not in IGNORED_COLUMNS],
        )
    else:
        assert topic in TOPICS_OF_INTEREST, f"{topic} is not a valid topic."
        logging.info(f"Going to extract gnews data about topic {topic}")

        google_news = GNews_wo_import()
        json_resp = google_news.get_news(topic)

        articles = [google_news.get_full_article(r['url']) for r in json_resp]
        logging.info(articles)
        articles = [article for article in articles if article is not None]
        logging.info(articles)
        gnews_df = pd.DataFrame([x.__dict__ for x in articles])
        gnews_df = gnews_df[~gnews_df.country.isin(IGNORED_COLUMNS)]

    upload_to_minio(
        "minioadmin",
        "minioadmin",
        "host.docker.internal:9000",
        "de-data-bronze",
        gnews_df,
        "data.csv",
    )
