from platform import libc_ver
from site import execsitecustomize
from waterquality.WaterQuality import DWWaterQuality
import os
from pathlib import Path

__version__ = "1.1.5"

print(f"Initializing waterquality package (version={__version__})")

# try to find waterdetect
try:
    import waterdetect

    print(f"Waterdetect version: {waterdetect.__version__}")
except Exception as e:
    print("Waterdetect not found")
    print(e)


def correct_proj_path():
    """
    Correct the path for the proj.db in environment variables
    """

    print("Trying to locate the proj.db inside GDAL.")

    # get the gdal path
    gdal_path = Path(os.environ["GDAL_DATA"])

    # test proj inside gdal
    proj_path = gdal_path / "proj"
    if not (proj_path / "proj.db").exists():
        proj_path = gdal_path.parent / "proj"

        if not (proj_path / "proj.db").exists():
            print(f"Could not find proj.db")
            return

    os.environ["PROJ_LIB"] = proj_path.as_posix()


# # correct the GDAL environment
# if "PROJ_LIB" in os.environ:
#     proj_path = Path(os.environ["PROJ_LIB"])
#     if not proj_path.exists():
#         correct_proj_path()
# else:
#     correct_proj_path()
