from functools import partial
import gzip
from io import BytesIO
import os
import geojson
import pandas as pd
import boto3
import botocore
from dotenv import load_dotenv


load_dotenv()


def filename_of(
    event_dt: pd.Timestamp, level: int, kind: str, compress: bool = True
) -> str:
    return f"{event_dt:%Y%m%d%H}_{level}hPa_{kind}.geojson{'.gz' if compress else ''}"


def save_to_file(file: str, data: geojson.GeoJSON, compress: bool = True) -> None:
    opener = (
        partial(gzip.open, mode="wt", encoding="UTF-8")
        if compress
        else partial(open, mode="w")
    )
    with opener(compress=compress)(file) as f:
        geojson.dump(data, f)


def save_to_s3(dt: pd.Timestamp, level: int, kind: str, data: geojson.GeoJSON) -> None:
    bucket = os.getenv("ENVIRONMENT_DATA_BUCKET")
    filename = f"{dt.year}/{filename_of(dt, level, kind, compress=True)}"
    gzip_buffer = BytesIO()

    with gzip.GzipFile(mode="w", fileobj=gzip_buffer) as gz_file:
        geojson_str = geojson.dumps(data)
        gz_file.write(geojson_str.encode("utf-8"))

    gzip_data = gzip_buffer.getvalue()
    _to_s3(bucket, filename, gzip_data)


def _to_s3(bucket: str, key: str, data: bytes) -> None:
    session = boto3.session.Session()
    client = session.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        config=botocore.config.Config(s3={"addressing_style": "virtual"}),
        region_name=os.getenv("S3_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
    )
