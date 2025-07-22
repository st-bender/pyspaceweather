# PySpaceWeather

**Python interface for space weather indices**

[![builds](https://github.com/st-bender/pyspaceweather/actions/workflows/ci_build_and_test.yml/badge.svg?branch=master)](https://github.com/st-bender/pyspaceweather/actions/workflows/ci_build_and_test.yml)
[![docs](https://readthedocs.org/projects/pyspaceweather/badge/?version=latest)](https://pyspaceweather.readthedocs.io/en/latest/?badge=latest)
[![package](https://img.shields.io/pypi/v/spaceweather.svg?style=flat)](https://pypi.org/project/spaceweather)
[![wheel](https://img.shields.io/pypi/wheel/spaceweather.svg?style=flat)](https://pypi.org/project/spaceweather)
[![pyversions](https://img.shields.io/pypi/pyversions/spaceweather.svg?style=flat)](https://pypi.org/project/spaceweather)
[![codecov](https://codecov.io/gh/st-bender/pyspaceweather/badge.svg)](https://codecov.io/gh/st-bender/pyspaceweather)
[![coveralls](https://coveralls.io/repos/github/st-bender/pyspaceweather/badge.svg)](https://coveralls.io/github/st-bender/pyspaceweather)
[![scrutinizer](https://scrutinizer-ci.com/g/st-bender/pyspaceweather/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/st-bender/pyspaceweather/?branch=master)

This python module interfaces the space weather data available at
<https://celestrak.com/SpaceData/>,
<https://kp.gfz-potsdam.de/en/data>,
and <https://omniweb.gsfc.nasa.gov/ow.html>.
It includes the geomagnetic Ap and Kp indices, both the 3h values and
the daily sum/averages.
The data also include the solar f10.7 cm radio fluxes,
the observed values as well as the 1 AU adjusted values,
daily values and the 81-day running means.
See [Data sources](#data-sources) below.

:warning: This package is in **beta** stage, that is, it works for the most part
and the interface should not change (much) in future versions.

Documentation is available at <https://pyspaceweather.readthedocs.io>.

## Install

### Requirements

- `numpy` - required
- `pandas` - required
- `requests` - required for updating the data files
- `pytest`, `pytest-mock` - optional, for testing

### spaceweather

A `pip` package called `spaceweather` is available from the
main package repository, and can be installed with:
```sh
$ pip install spaceweather
```
The latest development version can be installed
with [`pip`](https://pip.pypa.io) directly from github
(see <https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support>
and <https://pip.pypa.io/en/stable/reference/pip_install/#git>):

```sh
$ pip install [-e] git+https://github.com/st-bender/pyspaceweather.git
```

The other option is to use a local clone:

```sh
$ git clone https://github.com/st-bender/pyspaceweather.git
$ cd pyspaceweather
```
and then using `pip` (optionally using `-e`, see
<https://pip.pypa.io/en/stable/reference/pip_install/#install-editable>):

```sh
$ pip install [-e] .
```

or using `setup.py`:

```sh
$ python setup.py install
```

Optionally, test the correct function of the module with

```sh
$ py.test [-v]
```

or even including the [doctests](https://docs.python.org/library/doctest.html)
in this document:

```sh
$ py.test [-v] --doctest-glob='*.md'
```

## Usage

The python module itself is named `spaceweather` and is imported as usual
by calling

```python
>>> import spaceweather

```

### Celestrak

The module provides two functions to access the data from
[Celestrak](https://celestrak.com/SpaceData/),
`sw_daily()` for the daily data
as available from the website, and `ap_kp_3h()` for the 3h Ap and Kp values.
Both functions return `pandas.DataFrame`s.
When the data available in the packaged version are too old for the use case,
they can be updated by passing `update=True` to both functions, or by calling
`update_data()` explicitly.

```python
>>> import spaceweather as sw
>>> df_d = sw.sw_daily()
>>> print(df_d.loc["2000-01-01"].Apavg)
30.0
>>> df_3h = sw.ap_kp_3h()
>>> df_3h.loc["2000-01-01 01:30:00"]
Ap    56.0
Kp     5.3
Name: 2000-01-01 01:30:00, dtype: float64
>>> # All 3h values for one day
>>> df_3h.loc["2000-01-01"]
                     Ap   Kp
2000-01-01 01:30:00  56  5.3
2000-01-01 04:30:00  39  4.7
2000-01-01 07:30:00  27  4.0
2000-01-01 10:30:00  18  3.3
2000-01-01 13:30:00  32  4.3
2000-01-01 16:30:00  15  3.0
2000-01-01 19:30:00  32  4.3
2000-01-01 22:30:00  22  3.7

```

### GFZ

The "GFZ" module supports the ascii and WDC files as offered by the
[GFZ German Research Centre for Geosciences](https://www.gfz-potsdam.de/en/)
on their [data page](https://kp.gfz-potsdam.de/en/data).
In contrast to the official python client, this module reads the data
from the (downloaded) files and does not access the web service API.
The interface is mostly the same as for the "Celestrak" data:

```python
>>> import spaceweather as sw
>>> df_d = sw.gfz_daily()
>>> print(df_d.loc["2000-01-01"].Apavg)
30.0
>>> df_3h = sw.gfz_3h()
>>> df_3h.loc["2000-01-01 01:30:00"]
Ap    56.000
Kp     5.333
Name: 2000-01-01 01:30:00, dtype: float64

```

Currently, the data are not included in the package, downloads can be triggered
by passing `update=True` to `sw.gfz_daily()` or by running `sw.update_gfz()`.
The lower-level interface functions are called `read_gfz(<filename>)`
for the ascii `.txt` files, and `read_gfz_wdc(<filename>)` for the WDC format.
They can also be used directly for reading already downloaded data files
outside of the package's data directory.

```python
>>> import spaceweather as sw
>>> df_d = sw.read_gfz("./tests/Kp_ap_Ap_SN_F107_since_2024.txt")
>>> print(df_d.loc["2024-01-01"].Apavg)
10.0

```

The data format for the GFZ [Hpo indices](https://kp.gfz-potsdam.de/en/hp30-hp60)
Hp30 and Hp60 is also supported.
For downloading and updating the local Hp30 and Hp60 data files,
use `sw.update_gfz_hp30()` and `sw.update_gfz_hp60()`.
For reading individual files, use `read_gfz_hp(<filename>)`.

```python
>>> import spaceweather as sw
>>> df_hp30 = sw.read_gfz_hp("./tests/Hp30_ap30_nowcast.txt")
>>> df_hp30.loc["2025-07-01 00:15:00"]
year       2025.000000
month         7.000000
day           1.000000
hh_h          0.000000
hh_m          0.250000
days      34150.000000
days_m    34150.011719
Hp            3.000000
ap           15.000000
D             0.000000
Name: 2025-07-01 00:15:00, dtype: float64

>>> df_hp60 = sw.read_gfz_hp("./tests/Hp60_ap60_nowcast.txt")
>>> df_hp60.loc["2025-07-01 00:30:00"]
year       2025.000000
month         7.000000
day           1.000000
hh_h          0.000000
hh_m          0.500000
days      34150.000000
days_m    34150.019531
Hp            3.333000
ap           18.000000
D             0.000000
Name: 2025-07-01 00:30:00, dtype: float64

```

To get a complete combined historic and nowcast dataset, use `sw.gfz_daily()`
by passing the Hp30 or Hp60 file locations and setting `gfz_format` to "hp30" or "hp60".

```python
>>> import spaceweather as sw
>>> df_d = sw.gfz_daily(
... 	gfzpath_all=sw.HP30_PATH_ALL,
... 	gfzpath_30d=sw.HP30_PATH_30D,
... 	gfz_format="hp30",
... )
>>> df_d.loc["2025-07-01 00:15:00"]
year       2025.000000
month         7.000000
day           1.000000
hh_h          0.000000
hh_m          0.250000
days      34150.000000
days_m    34150.011719
Hp            3.000000
ap           15.000000
D             0.000000
Name: 2025-07-01 00:15:00, dtype: float64

```

### OMNI

The [OMNI](https://omniweb.gsfc.nasa.gov/ow.html) 1-hour yearly data
are accessible via `omnie_hourly(<year>)` or `read_omnie(<file>)`.
Both functions should work with the OMNI2 standard and extended text files.
If the data are not already available locally, they can be cached by passing
`cache=True` to that function or by calling `cache_omnie(<year>)` explicitly.
As for the Celestrak data, `pandas.DataFrame`s are returned.

```python
>>> import spaceweather as sw
>>> df_h = sw.omnie_hourly(2000)  # doctest: +SKIP
>>> # or with automatic caching (downloading)
>>> df_h = sw.omnie_hourly(2000, cache=True)  # doctest: +SKIP

```

If the data are already available locally, you can point the parser
to that location:

```python
>>> import spaceweather as sw
>>> df_h = sw.omnie_hourly(2000, local_path="/path/to/omni/data/")  # doctest: +SKIP

```

Another option is to provide a filename directly to `read_omnie()`:

```python
>>> import spaceweather as sw
>>> df = sw.read_omnie("/path/to/omni/data/file.dat")  # doctest: +SKIP

```


### Reference

Basic class and method documentation is accessible via `pydoc`:

```sh
$ pydoc spaceweather
$ pydoc spaceweather.celestrak
$ pydoc spaceweather.gfz
$ pydoc spaceweather.omni
```

## License

This python interface is free software: you can redistribute it or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 (GPLv2), see [local copy](./COPYING.GPLv2)
or [online version](http://www.gnu.org/licenses/gpl-2.0.html).

## Data sources

### Celestrak

The "celestrak" data can be found at <https://celestrak.com/SpaceData/>
and is included with kind permission from Dr. T.S. Kelso at
[celestrak](https://celestrak.com),
for details see the included [COPYING.data](COPYING.data) file.

The data sources and file format are described at
<http://celestrak.com/SpaceData/SpaceWx-format.php>
(see [file_format.txt](file_format.txt) for a local copy of the format description).

### GFZ

The "GFZ" data are provided as tabulated ascii files
([format description](https://kp.gfz-potsdam.de/app/format/Kp_ap_Ap_SN_F107_format.txt),
[local copy](gfz_Kp_ap_Ap_SN_F107_format.txt))
and in [WDC format](https://kp.gfz-potsdam.de/app/format/wdc_fmt.txt)
([local copy](gfz_wdc_fmt.txt))
by the
[GFZ German Research Centre for Geosciences](https://www.gfz-potsdam.de/en/)
on their official [data webpage](https://kp.gfz-potsdam.de/en/data).
The data have the doi: [10.5880/Kp.0001](https://doi.org/10.5880/Kp.0001),
and they are provided under the "Creative Commons attribution license"
[CC-by 4.0](https://creativecommons.org/licenses/by/4.0/)
(local copy [COPYING.CCby4.0](COPYING.CCby4.0)).

The "GFZ" Hp30 and Hp60 data are provided as tabulated ascii files
([Hp30 format](https://kp.gfz-potsdam.de/app/format/Hpo_Hp30_format.txt),
[local copy](gfz_Hpo_Hp30_format.txt);
[Hp60 format](https://kp.gfz-potsdam.de/app/format/Hpo_Hp60_format.txt),
[local copy](gfz_Hpo_Hp60_format.txt)).
The Hpo data are available from
<https://kp.gfz-potsdam.de/en/hp30-hp60> and via the
doi: [10.5880/Hpo.0003](https://doi.org/10.5880/Hpo.0003).

When using data from the GFZ Potsdam, consider to cite the following publications,
see also [COPYING.gfz](COPYING.gfz) for details:

Matzka, J., Stolle, C., Yamazaki, Y., Bronkalla, O., & Morschhauser, A. (2021),
The geomagnetic Kp index and derived indices of geomagnetic activity,
Space Weather, volume 19, issue 5, e2020SW002641. <https://doi.org/10.1029/2020SW002641>

Yamazaki, Y., Matzka, J., da Silva, M.V., Kervalishvili, G., Korte, M., Rauberg, J., (2024),
Assessment of geomagnetic activity for the Kp=9 "Gannon Storm" in May 2024 based on version 3.0 Hpo Indices.
ESS Open Archive, <https://doi.org/10.22541/essoar.171838396.68563140/v1>

### OMNI

This package includes part of the hourly-resolved OMNI data,
accessible through <https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/>,
and it enables easy downloading of it.
The file format is described at
<https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2.text>
(local copy [omni_format.txt](omni_format.txt))
and the "extended" format at
<https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/extended/aareadme_extended>
(local copy [omnie_format.txt](omnie_format.txt)).

If you use the OMNI data in your work, please read [COPYING.omni](COPYING.omni)
carefully and cite the following publication:

King, Joseph H. and Natalia E. Papitashvili,
Solar wind spatial scales in and comparisons of hourly Wind and ACE plasma and magnetic field data,
J. Geophys. Res., 110, A02104, 2005.

Please acknowledge the OMNI sources, using the following DOIs for the OMNI datasets:

Papitashvili, Natalia E. and King, Joseph H. (2022), "OMNI 1-min Data" [Data set],
NASA Space Physics Data Facility, <https://doi.org/10.48322/45bb-8792>

Papitashvili, Natalia E. and King, Joseph H. (2022), "OMNI 5-min Data" [Data set],
NASA Space Physics Data Facility, <https://doi.org/10.48322/gbpg-5r77>

Papitashvili, Natalia E. and King, Joseph H. (2022), "OMNI Hourly Data" [Data Set],
NASA Space Physics Data Facility, <https://doi.org/10.48322/1shr-ht18>

Papitashvili, Natalia E. and King, Joseph H. (2022), "OMNI Daily Data" [Data set],
NASA Space Physics Data Facility, <https://doi.org/10.48322/5fmx-hv56>

Papitashvili, Natalia E. and King, Joseph H. (2022), "OMNI 27-Day Data" [Data set],
NASA Space Physics Data Facility, <https://doi.org/10.48322/nmh3-jf75>

The OMNI data are also available from CDAWeb, and thus available via various other methods
<https://cdaweb.gsfc.nasa.gov/alternative_access_methods.html>
In particular, you might find our Python web service library useful
<https://pypi.org/project/cdasws>
Or through the HAPI streaming protocol <https://github.com/hapi-server/client-python>
