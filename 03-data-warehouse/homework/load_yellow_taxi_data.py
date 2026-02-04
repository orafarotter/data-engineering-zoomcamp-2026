from __future__ import annotations
import argparse
import logging
import os
import tempfile
from google.cloud import storage
import requests

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
MONTHS = range(1, 7)  # January - June

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def month_str(m: int) -> str:
    return f"{m:02d}"


def build_filename(year: int, month: int) -> str:
    return f"yellow_tripdata_{year}-{month_str(month)}.parquet"


def build_url(year: int, month: int) -> str:
    return f"{BASE_URL}/{build_filename(year, month)}"


def download_parquet(url: str, target_path: str, chunk_size: int = 4 * 1024 * 1024) -> None:
    logger.info("Downloading %s", url)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)


def upload_to_gcs(bucket_name: str, destination_blob_name: str, source_file_path: str) -> None:
    logger.info("Uploading %s to gs://%s/%s", source_file_path,
                bucket_name, destination_blob_name)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.chunk_size = 10 * 1024 * 1024
    blob.upload_from_filename(source_file_path)
    logger.info("Uploaded gs://%s/%s", bucket_name, destination_blob_name)


def load_local_dotenv(path: str = ".env") -> None:
    """Load environment variables from a local .env file.

    Attempts to use python-dotenv if available, otherwise falls back to a minimal parser.
    """
    try:
        from dotenv import load_dotenv as _load_dotenv  # type: ignore
        _load_dotenv(path)
        logger.info("Loaded environment from %s (python-dotenv)", path)
    except Exception:
        if os.path.exists(path):
            logger.info("Loading %s manually", path)
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    # do not override existing env vars
                    if key not in os.environ:
                        os.environ[key] = val


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Jan-Jun yellow taxi parquet files and upload to GCS")
    parser.add_argument("--year", type=int, default=None,
                        help="Year to download (default: 2024 or YEAR env var)")
    parser.add_argument("--bucket", default=None,
                        help="GCS bucket name (or set GCS_BUCKET env var)")
    parser.add_argument("--prefix", default=None,
                        help="GCS prefix (folder) to store files, default 'yellow/' or GCS_PREFIX env var")
    parser.add_argument("--credentials", default=None,
                        help="Path to service account JSON credentials (optional)")
    return parser.parse_args()


def main() -> None:
    # load .env early so environment values can be used as defaults
    load_local_dotenv()

    args = parse_args()

    year = args.year or int(os.environ.get("YEAR", "2024"))
    bucket = args.bucket or os.environ.get("GCS_BUCKET")
    prefix = args.prefix or os.environ.get("GCS_PREFIX", "yellow/")

    if not bucket:
        logger.error(
            "No GCS bucket provided. Set GCS_BUCKET in environment or provide --bucket.")
        raise SystemExit(1)

    # Optionally set credentials for this run
    old_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if args.credentials:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.credentials

    try:
        for month in MONTHS:
            filename = build_filename(year, month)
            url = build_url(year, month)
            gcs_path = f"{prefix.rstrip('/')}/{filename}"

            with tempfile.NamedTemporaryFile(prefix=filename + "-", suffix="", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                download_parquet(url, tmp_path)
                upload_to_gcs(bucket, gcs_path, tmp_path)
            except Exception:
                logger.exception("Failed for %s", url)
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
    finally:
        # restore previous credentials env var
        if args.credentials:
            if old_creds is not None:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = old_creds
            else:
                os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)


if __name__ == "__main__":
    main()
