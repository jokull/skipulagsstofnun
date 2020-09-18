# skipulagsstofnun

Library to lookup polygons, coordinates and metadata of approved local site plans in Iceland.

Used by [Planitor](https://www.planitor.io).

```python
>>> from skipulagsstofnun import plans
>>> plan = plans.get_plan()
>>> plan = plans.get_plan(64.1525571, -21.9508792)
>>> plan
{'id': 'skipulag_deiliskipulag.198969', 'type': 'Feature', 'skipnr': '8136', 'nrsveitarf': '0', 'sveitarfelag': 'Reykjavíkurborg', 'heiti': 'Deiliskipulag stgr. 1.116 og 1.115.3, Slippa- og Ellingsensreitur', 'skipstig': 'deiliskipulag', 'malsmed': 'nytt', 'dagsinnsett': None, 'dagsleidrett': datetime.date(2016, 4, 14), 'gagnaeigandi': 'Skipulagsstofnun', 'dagsheimild': None, 'heimild': None, 'nakvaemnix': '0', 'vinnslufer': None}
```

You can construct a link to a page hosted by Skipulagsstofnun with the PDF
scans for this local site plan.

`http://skipulagsaaetlanir.skipulagsstofnun.is/skipulagvefur/display.aspx?numer={skipnr}``
