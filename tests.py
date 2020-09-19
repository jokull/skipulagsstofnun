from shapely.geometry import Polygon
from skipulagsstofnun import plans


def test_match():
    shape, plan = plans.get_plan(64.1525571, -21.9508792)
    assert isinstance(shape, Polygon)
    assert isinstance(plan, dict)


def test_no_match():
    shape, plan = plans.get_plan(0, 0)
    assert shape is None
    assert plan is None
