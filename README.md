# PySpaceWeather

**Python interface for space weather indices**

[![builds](https://travis-ci.com/st-bender/pyspaceweather.svg?branch=master)](https://travis-ci.com/st-bender/pyspaceweather)
[![docs](https://readthedocs.org/projects/pyspaceweather/badge/?version=latest)](https://pyspaceweather.readthedocs.io/en/latest/?badge=latest)
[![package](https://img.shields.io/pypi/v/spaceweather.svg?style=flat)](https://pypi.org/project/spaceweather)
[![wheel](https://img.shields.io/pypi/wheel/spaceweather.svg?style=flat)](https://pypi.org/project/spaceweather)
[![pyversions](https://img.shields.io/pypi/pyversions/spaceweather.svg?style=flat)](https://pypi.org/project/spaceweather)
[![codecov](https://codecov.io/gh/st-bender/pyspaceweather/badge.svg)](https://codecov.io/gh/st-bender/pyspaceweather)
[![coveralls](https://coveralls.io/repos/github/st-bender/pyspaceweather/badge.svg)](https://coveralls.io/github/st-bender/pyspaceweather)
[![scrutinizer](https://scrutinizer-ci.com/g/st-bender/pyspaceweather/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/st-bender/pyspaceweather/?branch=master)

This python module interfaces the space weather indices available at
<https://celestrak.com/SpaceData/>.
It includes the geomagnetic Ap and Kp indices, both the 3h values and
the daily sum/averages.
The data also include the solar f10.7 cm radio fluxes,
the observed values as well as the 1 AU adjusted values,
daily values and the 81-day running means.
The data sources and file format are described at
<http://celestrak.com/SpaceData/SpaceWx-format.php>
(see [file_format.txt](file_format.txt) for a local copy of the format description).

:warning: This package is in **alpha** stage, that is, it may or
may not work, and the interface might change in future versions.

Documentation is available at <https://pyspaceweather.readthedocs.io>.

## Install

### Requirements

- `numpy` - required
- `pytest`, `pytest-mock` - optional, for testing

### spaceweather

An **experimental** `pip` package called `spaceweather` is available from the
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

The python module itself is named `spaceweather` and is imported as usual.
This module provides mainly two functions `sw_daily()` for the daily data
as available from the website, and `ap_kp_3h()` for the 3h Ap and Kp values.
Both functions return `pandas.DataFrame`s.
The index data file can be updated on request by calling `update_data()`,
when the data available in the packaged version are too old.

```python
>>> import spaceweather as sw
>>> df_d = sw.sw_daily()
>>> df_d.loc["2000-01-01"].Apavg
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

Basic class and method documentation is accessible via `pydoc`:

```sh
$ pydoc spaceweather
```

# License

This python interface is free software: you can redistribute it or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 (GPLv2), see [local copy](./COPYING.GPLv2)
or [online version](http://www.gnu.org/licenses/gpl-2.0.html).

The original data can be found at <https://celestrak.com/SpaceData/>
and is included with kind permission from Dr. T.S. Kelso at
[celestrak](https://celestrak.com),
for details see the included [COPYING.data](COPYING.data) file.
