import datetime as dt
from pathlib import Path

import fiona
from shapely.geometry import shape, Point


shapefile = Path(__file__).resolve().parent / "plans.shp"

if not shapefile.is_file():
    raise ValueError("Plans not generated, please run create_shapefile.py")


def process_date(s):
    if s == "00000000":
        return None
    else:
        return dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))


FIELDNAME_MAP = dict(
    (
        ("sveitarfel", "sveitarfelag"),
        ("gagnaeigan", "gagnaeigandi"),
        ("dagsheimil", "dagsheimild"),
        ("dagsleidre", "dagsleidrett"),
        ("dagsinnset", "dagsinnsett"),
    )
)


class DB:

    _plans = {}

    def __init__(self, path):
        with fiona.open(path, "r") as fp:
            self.schema = fp.schema
            for f in fp:
                properties = {}
                for key, value in f["properties"].items():
                    if key in FIELDNAME_MAP:
                        key = FIELDNAME_MAP[key]
                    if key in ("dagsinnsett", "dagsleidrett", "dagsheimild"):
                        value = value.replace("-", "")
                        try:
                            value = process_date(value)
                        except Exception as e:
                            value = None
                    properties[key] = value
                id_ = int(properties["skipnr"])
                polygon = shape(f["geometry"])
                self._plans[id_] = polygon, properties

    def get_plan(self, x, y):
        point = Point(x, y)
        for polygon, properties in self._plans.values():
            if point.within(polygon):
                return properties


plans = DB(str(shapefile))
