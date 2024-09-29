import gzip
from io import BytesIO
import os
import geojson
from boto3.session import Session
from botocore.config import Config
import s3fs
import xarray as xr
from dotenv import load_dotenv

from weather_cases.environment.configs import EventDataRequest
from weather_cases.environment.exceptions import DataNotFoundException
from weather_cases.environment.types import XArrayData


load_dotenv()


S3_FILE_SYSTEM = s3fs.S3FileSystem(
    key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
)


def save_geojson(
    data_request: EventDataRequest, kind: str, data: geojson.GeoJSON
) -> None:
    gzip_buffer = BytesIO()
    filename = data_request.to_s3_location(kind, "geojson.gz")

    with gzip.GzipFile(mode="w", fileobj=gzip_buffer) as gz_file:
        geojson_str = geojson.dumps(data)
        gz_file.write(geojson_str.encode("utf-8"))

    gzip_data = gzip_buffer.getvalue()
    _write_s3_obj(filename, gzip_data)


def save_dataset(
    data_request: EventDataRequest,
    kind: str,
    data: XArrayData,
) -> None:
    s3_path = data_request.full_s3_location_path(kind, "zarr")
    store = s3fs.S3Map(root=s3_path, s3=S3_FILE_SYSTEM)
    data.to_zarr(store=store, mode="w", consolidated=True)


def read_dataset(data_request: EventDataRequest, kind: str) -> xr.Dataset:
    try:
        s3_path = data_request.full_s3_location_path(kind, "zarr")
        store = s3fs.S3Map(root=s3_path, s3=S3_FILE_SYSTEM, check=False)
        return xr.open_zarr(store, chunks=None)  # type: ignore
    except FileNotFoundError:
        raise DataNotFoundException("Data not found")


def _write_s3_obj(key: str, data: bytes) -> None:
    session = Session()
    client = session.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        config=Config(s3={"addressing_style": "virtual"}),
        region_name=os.getenv("S3_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    client.put_object(
        Bucket=os.getenv("S3_BUCKET_NAME"),
        Key=key,
        Body=data,
        ACL="public-read",
    )
