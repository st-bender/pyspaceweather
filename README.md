# Python interface for space weather indices

[![builds](https://travis-ci.com/st-bender/pyspaceweather.svg?branch=master)](https://travis-ci.com/st-bender/pyspaceweather)
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

## Install

### Requirements

- `numpy` - required
- `pytest` - optional, for testing

### pyspaceweather

As binary package support is limited, pyspaceweather can be installed
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
The index file will be downloaded locally on the first run.

```python
>>> import spaceweather as sw
>>> df_d = sw.sw_daily()
>>> df_d.loc["2000-01-01"].Apavg
30.0
>>> df_3h = sw.ap_kp_3h()
>>> df_3h.loc["2000-01-01 01:30:00"]
                     Ap   Kp
2000-01-01 01:30:00  56  5.3

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
