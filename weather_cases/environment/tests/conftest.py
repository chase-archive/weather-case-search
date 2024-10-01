import pytest
import xarray as xr


@pytest.fixture
def sample_height_ds():
    return xr.Dataset(
        data_vars={
            "Z": xr.DataArray(
                data=[[10, 15, 13], [11, 11, 16], [20, 13, 12]],
                dims=("latitude", "longitude"),
                coords={"latitude": [1, 2, 3], "longitude": [1, 2, 3]},
            )
        }
    )
