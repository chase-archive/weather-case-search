import gzip
from io import BytesIO
import os
import geojson
import pandas as pd
import boto3
import botocore
import s3fs
import xarray as xr
from dotenv import load_dotenv


load_dotenv()


def s3_location(
    event_id: str, dt: pd.Timestamp, level: int, kind: str, filetype: str
) -> str:
    return f"{event_id}/{dt:%Y-%m-%d}/{dt:%H}/{level}/{kind}.{filetype}"


def save_geojson(
    event_id: str, dt: pd.Timestamp, level: int, kind: str, data: geojson.GeoJSON
) -> None:
    bucket = os.getenv("S3_BUCKET_NAME")
    filename = s3_location(event_id, dt, level, kind, "geojson.gz")
    gzip_buffer = BytesIO()

    with gzip.GzipFile(mode="w", fileobj=gzip_buffer) as gz_file:
        geojson_str = geojson.dumps(data)
        gz_file.write(geojson_str.encode("utf-8"))

    gzip_data = gzip_buffer.getvalue()
    _to_s3(bucket, filename, gzip_data)


def save_dataset(
    event_id: str,
    dt: pd.Timestamp,
    level: int,
    kind: str,
    data: xr.Dataset | xr.DataArray,
) -> None:
    bucket = os.getenv("S3_BUCKET_NAME")
    filename = s3_location(event_id, dt, level, kind, "zarr")

    s3 = s3fs.S3FileSystem(
        key=os.getenv("AWS_ACCESS_KEY_ID"),
        secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    )
    s3_path = f"s3://{bucket}/{filename}"
    store = s3fs.S3Map(root=s3_path, s3=s3)
    data.to_zarr(store=store, mode="w", consolidated=True)
    return store


def read_dataset(event_id: str, dt: pd.Timestamp, level: int, kind: str) -> xr.Dataset:
    bucket = os.getenv("S3_BUCKET_NAME")
    filename = s3_location(event_id, dt, level, kind, "zarr")

    s3 = s3fs.S3FileSystem(
        key=os.getenv("AWS_ACCESS_KEY_ID"),
        secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    )
    s3_path = f"s3://{bucket}/{filename}"
    store = s3fs.S3Map(root=s3_path, s3=s3, check=False)
    return xr.open_zarr(store, chunks=None)


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
