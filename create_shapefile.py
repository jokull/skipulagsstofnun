from typing import List, Tuple, Dict
from pathlib import Path
import math
from collections import namedtuple
from decimal import Decimal
import json

import requests
import typer
import fiona
import shapely
from shapely.geometry import Polygon, mapping


def isnet93_to_wgs84(xx: float, yy: float):
    x = xx
    y = yy
    a = 6378137.0
    f = 1 / 298.257222101
    lat1 = 64.25
    lat2 = 65.75
    latc = 65.00
    lonc = 19.00
    eps = 0.00000000001

    def fx(p):
        return a * math.cos(p / rho) / math.sqrt(1 - math.pow(e * math.sin(p / rho), 2))

    def f1(p):
        return math.log((1 - p) / (1 + p))

    def f2(p):
        return f1(p) - e * f1(e * p)

    def f3(p):
        return pol1 * math.exp((f2(math.sin(p / rho)) - f2sin1) * sint / 2)

    rho = 45 / math.atan2(1.0, 1.0)
    e = math.sqrt(f * (2 - f))
    dum = f2(math.sin(lat1 / rho)) - f2(math.sin(lat2 / rho))
    sint = 2 * (math.log(fx(lat1)) - math.log(fx(lat2))) / dum
    f2sin1 = f2(math.sin(lat1 / rho))
    pol1 = fx(lat1) / sint
    polc = f3(latc) + 500000.0
    peq = (
        a
        * math.cos(latc / rho)
        / (sint * math.exp(sint * math.log((45 - latc / 2) / rho)))
    )
    pol = math.sqrt(math.pow(x - 500000, 2) + math.pow(polc - y, 2))
    lat = 90 - 2 * rho * math.atan(math.exp(math.log(pol / peq) / sint))
    lon = 0
    fact = rho * math.cos(lat / rho) / sint / pol
    fact = rho * math.cos(lat / rho) / sint / pol
    delta = 1.0
    while math.fabs(delta) > eps:
        delta = (f3(lat) - pol) * fact
        lat += delta
    lon = -(lonc + rho * math.atan((500000 - x) / (polc - y)) / sint)

    return round(lat, 7), round(lon, 7)


COLS = []


def get_params() -> List[Tuple[str, str]]:
    return [
        ("service", "wfs"),
        ("request", "GetFeature"),
        ("version", "1.1.0"),
        ("typename", "gogn_notenda:skipulag_deiliskipulag"),
        ("maxfeatures", "3000"),
        ("outputFormat", "text/javascript"),
        ("format_options", "callback:loadFeatures"),
        ("srsname", "EPSG:3057"),
        ("true", "jQuery1124045402241304828983_1599570770053"),
        ("_", "1599570770063"),
    ]


Box = namedtuple("Box", ("left", "top", "right", "bottom"))

# Draw a large box around Iceland, which is then broken down into tiles
iceland = Box(
    Decimal("49467.65647151711"),  # Left
    Decimal("259123.41317910506"),  # Top
    Decimal("952578.2799028917"),  # Right
    Decimal("732903.7128932988"),  # Bottom
)


x_tiles, y_tiles = (6, 6)


width = (iceland.right - iceland.left) / x_tiles
height = (iceland.bottom - iceland.top) / y_tiles


def get_response(tile) -> dict:

    geom = ",".join(str(_) for _ in tile)
    params = get_params() + [("CQL_FILTER", f"BBOX(geom,{geom})")]

    response = requests.get(
        "http://www.map.is/webservice/proxies/geoserver.php",
        params=dict(params),
    )

    json_string = response.text[len("loadFeatures(") : -1]
    return json.loads(json_string)


def iter_boxes():
    for y in range(0, y_tiles):
        for x in range(0, x_tiles):
            x_start = iceland.left + (width * x)
            y_start = iceland.top + (height * y)
            yield x, y, Box(x_start, y_start, x_start + width, y_start + height)


PROPERTIES = {
    "id": "str",
    "type": "str",
    "skipnr": "str",
    "nrsveitarf": "str",
    "sveitarfel": "str",
    "heiti": "str",
    "skipstig": "str",
    "malsmed": "str",
    "dagsinnset": "str",
    "dagsleidre": "str",
    "gagnaeigan": "str",
    "dagsheimil": "str",
    "heimild": "str",
    "nakvaemnix": "str",
    "vinnslufer": "str",
}


def process_feature(feature) -> Tuple[Dict[str, str], Polygon]:
    """Notice that the character limit for shapefile property keys is 10 characters
    therefore dagsheimild > dagsheimil.
    """
    props = feature["properties"]
    d = {
        "id": feature["id"],
        "type": feature["type"],
        "skipnr": props["skipnr"],
        "nrsveitarf": props["nrsveitarf"],
        "sveitarfel": props["sveitarfelag"],
        "heiti": props["heiti"],
        "skipstig": props["skipstig"],
        "malsmed": props["malsmed"],
        "dagsinnset": props["dagsinnset"],
        "dagsleidre": props["dagsleidre"],
        "gagnaeigan": props["gagnaeigandi"],
        "dagsheimil": props["dagsheimild"],
        "heimild": props["heimild"],
        "nakvaemnix": props["nakvaemnix"],
        "vinnslufer": props["vinnslufer"],
    }
    return d, Polygon(
        [isnet93_to_wgs84(x, y) for x, y in feature["geometry"]["coordinates"][0]]
    )


def main(
    db_path: Path = typer.Option(
        default="skipulagsstofnun/plans.shp",
        writable=True,
        resolve_path=True,
        dir_okay=False,
    )
):

    # Delete previous db file
    if db_path.is_file():
        if input(f"{db_path} exists, overwrite? (y/n): ").lower().startswith("y"):
            db_path.unlink()

    with fiona.open(
        db_path,
        "w",
        "ESRI Shapefile",
        schema={"geometry": "Polygon", "properties": PROPERTIES},
    ) as fp:
        for x, y, tile in iter_boxes():
            response = get_response(tile)
            if not response["features"]:
                continue
            for feature in response["features"]:
                props, polygon = process_feature(feature)
                fp.write(
                    {
                        "geometry": mapping(polygon),
                        "properties": props,
                    }
                )


if __name__ == "__main__":
    typer.run(main)


"""Example API feature object

{
    "type": "Feature",
    "id": "skipulag_deiliskipulag.165455",
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [436959.2998, 325049.5761],
                [437189.8016, 325198.4649],
                [437206.3447, 325200.1192],
                [437204.6904, 325183.0245],
                [437155.6123, 325034.6873],
                [437125.8345, 324998.2922],
                [437070.6906, 324962.4487],
                [437007.275, 324992.7778],
                [436959.2998, 325049.5761],
            ]
        ],
    },
    "geometry_name": "geom",
    "properties": {
        "audkenni": "",
        "skipnr": "6495",
        "sveitarfelag": "Vestmannaeyjabær",
        "nrsveitarf": "8000",
        "heiti": "Deiliskipulag iðanaðarsvæðis IS-3",
        "skipstig": "deiliskipulag",
        "malsmed": "nytt",
        "dagsinnset": "00000000",
        "dagsleidre": "20160414",
        "gagnaeigandi": "Skipulagsstofnun",
        "dagsheimild": "00000000",
        "heimild": "",
        "nakvaemnix": "0",
        "vinnslufer": "",
    },
}

"""
