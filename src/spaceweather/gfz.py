# Copyright (c) 2020--2024 Stefan Bender
#
# This module is part of pyspaceweather.
# pyspaceweather is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying COPYING.GPLv2 file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python interface for space weather indices from GFZ Potsdam

GFZ space weather indices ASCII file parser for python [#]_.
Includes parser for the GFZ ASCII files, files in WDC format,
and for the Hpo 30 and 60 minute ASCII files [#]_.
For the file formats, see the `gfz_xxx_format.txt` files.

.. [#] https://kp.gfz-potsdam.de/en/
.. [#] https://kp.gfz-potsdam.de/en/hp30-hp60
"""
import os
import logging
from warnings import warn

import numpy as np
import pandas as pd

from .core import _assert_file_exists, _dl_file, _resource_filepath

__all__ = [
	"gfz_daily", "gfz_3h", "read_gfz",
	"read_gfz_hp",
	"get_gfz_age", "update_gfz",
	"update_gfz_hp30", "update_gfz_hp60",
	"GFZ_PATH_ALL", "GFZ_PATH_30D",
	"HP30_PATH_ALL", "HP30_PATH_30D",
	"HP60_PATH_ALL", "HP60_PATH_30D",
]

GFZ_URL_ALL = "https://kp.gfz-potsdam.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt"
GFZ_URL_30D = "https://kp.gfz-potsdam.de/app/files/Kp_ap_Ap_SN_F107_nowcast.txt"
GFZ_FILE_ALL = os.path.basename(GFZ_URL_ALL)
GFZ_FILE_30D = os.path.basename(GFZ_URL_30D)
GFZ_PATH_ALL = _resource_filepath(GFZ_FILE_ALL)
GFZ_PATH_30D = _resource_filepath(GFZ_FILE_30D)

HP30_URL_ALL = "https://kp.gfz.de/app/files/Hp30_ap30_complete_series.txt"
HP30_URL_30D = "https://kp.gfz.de/app/files/Hp30_ap30_nowcast.txt"
HP30_FILE_ALL = os.path.basename(HP30_URL_ALL)
HP30_FILE_30D = os.path.basename(HP30_URL_30D)
HP30_PATH_ALL = _resource_filepath(HP30_FILE_ALL)
HP30_PATH_30D = _resource_filepath(HP30_FILE_30D)

HP60_URL_ALL = "https://kp.gfz.de/app/files/Hp60_ap60_complete_series.txt"
HP60_URL_30D = "https://kp.gfz.de/app/files/Hp60_ap60_nowcast.txt"
HP60_FILE_ALL = os.path.basename(HP60_URL_ALL)
HP60_FILE_30D = os.path.basename(HP60_URL_30D)
HP60_PATH_ALL = _resource_filepath(HP60_FILE_ALL)
HP60_PATH_30D = _resource_filepath(HP60_FILE_30D)


def get_gfz_age(gfzpath, relative=True):
	"""Age of the downloaded data file

	Retrieves the last update time of the given file or full path.

	Parameters
	----------
	gfzpath: str
		Filename to check, absolute path or relative to the current dir.
	relative: bool, optional, default True
		Return the file's age (True) or the last update time (False).

	Returns
	-------
	upd: pandas.Timestamp or pandas.Timedelta
		The last updated time or the file age, depending on the setting
		of `relative` above.
		Raises ``IOError`` if the file is not found.
	"""
	_assert_file_exists(gfzpath)
	with open(gfzpath) as fp:
		for line in fp:
			# forward to last line
			pass
	upd = pd.to_datetime(line[:10].replace(" ", "-"), utc=True)
	if relative:
		return pd.Timestamp.utcnow() - upd
	return upd


def update_gfz(
	min_age="1d",
	gfzpath_all=GFZ_PATH_ALL, gfzpath_30d=GFZ_PATH_30D,
	url_all=GFZ_URL_ALL, url_30d=GFZ_URL_30D,
):
	"""Update the local space weather index data

	Updates the local space weather index data from the website [#]_,
	given that the 30-day file is older than `min_age`,
	or the combined (large) file is older than 30 days.
	If the data is missing for some reason, a download will be attempted nonetheless.

	All arguments are optional and changing them from the defaults should
	neither be necessary nor is it recommended.

	.. [#] https://kp.gfz-potsdam.de/en/

	Parameters
	----------
	min_age: str, optional, default "1d"
		The time after which a new download will be attempted.
		The online data is updated every day, thus setting this value to
		a shorter time is not needed and not recommended.
	gfzpath_all: str, optional, default depending on package install location
		Filename for the large combined index file including the
		historic data, absolute path or relative to the current dir.
	gfzpath_30d: str, optional, default depending on package install location
		Filename for the 30-day (nowcast) index file, absolute path or relative
		to the current dir.
	url_all: str, optional, default `gfz.GFZ_URL_ALL`
		The url of the "historic" data file.
	url_30d: str, optional, default `gfz.GFZ_URL_30D`
		The url of the data file containing the indices for the last 30 days.

	Returns
	-------
	Nothing.
	"""
	def _update_file(gfzpath, url, min_age):
		if not os.path.exists(gfzpath):
			logging.info("{0} not found, downloading.".format(gfzpath))
			_dl_file(gfzpath, url)
			return
		if get_gfz_age(gfzpath) < pd.Timedelta(min_age):
			logging.info("not updating '{0}'.".format(gfzpath))
			return
		logging.info("updating '{0}'.".format(gfzpath))
		_dl_file(gfzpath, url)

	# Update the large file after 30 days
	_update_file(gfzpath_all, url_all, "30days")
	# Don't re-download before `min_age` has passed (1d)
	_update_file(gfzpath_30d, url_30d, min_age)


def update_gfz_hp30(
	min_age="1d",
	gfzpath_all=HP30_PATH_ALL, gfzpath_30d=HP30_PATH_30D,
	url_all=HP30_URL_ALL, url_30d=HP30_URL_30D,
):
	"""Updates the local Hp30 index data

	See Also
	--------
	update_gfz
	"""
	return update_gfz(
		min_age=min_age,
		gfzpath_all=gfzpath_all, gfzpath_30d=gfzpath_30d,
		url_all=url_all, url_30d=url_30d,
	)


def update_gfz_hp60(
	min_age="1d",
	gfzpath_all=HP60_PATH_ALL, gfzpath_30d=HP60_PATH_30D,
	url_all=HP60_URL_ALL, url_30d=HP60_URL_30D,
):
	"""Updates the local Hp60 index data

	See Also
	--------
	update_gfz
	"""
	return update_gfz(
		min_age=min_age,
		gfzpath_all=gfzpath_all, gfzpath_30d=gfzpath_30d,
		url_all=url_all, url_30d=url_30d,
	)


def read_gfz(gfzpath):
	"""Read and parse space weather index data file

	Reads the given file and parses it according to the space weather data format.

	Parameters
	----------
	gfzpath: str
		File to parse, absolute path or relative to the current dir.

	Returns
	-------
	gfz_df: pandas.DataFrame
		The parsed space weather data (daily values).
		Raises an ``IOError`` if the file is not found.

		The dataframe contains the following columns:

		"year", "month", "day":
			The observation date
		"bsrn":
			Bartels Solar Rotation Number.
			A sequence of 27-day intervals counted continuously from 1832 Feb 8.
		"rotd":
			Number of Day within the Bartels 27-day cycle (01-27).
		"Kp0", "Kp3", "Kp6", "Kp9", "Kp12", "Kp15", "Kp18", "Kp21":
			Planetary 3-hour Range Index (Kp) for 0000-0300, 0300-0600,
			0600-0900, 0900-1200, 1200-1500, 1500-1800, 1800-2100, 2100-2400 UT
		"Kpsum": Sum of the 8 Kp indices for the day.
			Expressed to the nearest third of a unit.
		"Ap0", "Ap3", "Ap6", "Ap9", "Ap12", "Ap15", "Ap18", "Ap21":
			Planetary Equivalent Amplitude (Ap) for 0000-0300, 0300-0600,
			0600-0900, 0900-1200, 1200-1500, 1500-1800, 1800-2100, 2100-2400 UT
		"Apavg":
			Arithmetic average of the 8 Ap indices for the day.
		"isn":
			International Sunspot Number.
			Records contain the Zurich number through 1980 Dec 31 and the
			International Brussels number thereafter.
		"f107_obs":
			Observed (unadjusted) value of F10.7.
		"f107_adj":
			10.7-cm Solar Radio Flux (F10.7) Adjusted to 1 AU.
			Measured at Ottawa at 1700 UT daily from 1947 Feb 14 until
			1991 May 31 and measured at Penticton at 2000 UT from 1991 Jun 01 on.
			Expressed in units of 10-22 W/m2/Hz.
		"D":
			Definitive indicator.
			0: Kp and SN preliminary
			1: Kp definitive, SN preliminary
			2: Kp and SN definitive
	"""
	_assert_file_exists(gfzpath)
	gfz = np.genfromtxt(
		gfzpath,
		skip_header=3,
		delimiter=[
		#  yy mm dd dd dm br db kp kp kp kp kp kp kp kp
			4, 3, 3, 6, 8, 5, 3, 7, 7, 7, 7, 7, 7, 7, 7,
		#  ap ap ap ap ap ap ap ap Ap sn f1 f2 def
			5, 5, 5, 5, 5, 5, 5, 5, 6, 4, 9, 9, 2,
		],
		dtype=(
			"i4,i4,i4,i4,f4,i4,i4,f4,f4,f4,f4,f4,f4,f4,"
			"f4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,f8,f8,i4,"
		),
		names=[
			"year", "month", "day", "days", "days_m", "bsrn", "rotd",
			"Kp0", "Kp3", "Kp6", "Kp9", "Kp12", "Kp15", "Kp18", "Kp21",
			"Ap0", "Ap3", "Ap6", "Ap9", "Ap12", "Ap15", "Ap18", "Ap21", "Apavg",
			"isn", "f107_obs", "f107_adj", "D",
		]
	)
	gfz = gfz[gfz["year"] != -1]
	ts = pd.to_datetime([
		"{0:04d}-{1:02d}-{2:02d}".format(yy, mm, dd)
		for yy, mm, dd in gfz[["year", "month", "day"]]
	])
	gfz_df = pd.DataFrame(gfz, index=ts)
	# Sum Kp for compatibility with celestrak dataframe
	kpns = list(map("Kp{0}".format, range(0, 23, 3)))
	gfz_df.insert(15, "Kpsum", gfz_df[kpns].sum(axis=1))
	return gfz_df


def read_gfz_hp(gfzhppath):
	"""Read and parse GFZ Hp30 and Hp60 index data file

	Reads the given file and parses it according to the Hp30 and Hp60 file format.
	File format descriptions in [#]_ and [#]_

	.. [#] https://kp.gfz-potsdam.de/app/format/Hpo_Hp30.txt
	.. [#] https://kp.gfz-potsdam.de/app/format/Hpo_Hp60.txt

	Parameters
	----------
	gfzhppath: str
		File to parse, absolute path or relative to the current dir.

	Returns
	-------
	hp_df: pandas.DataFrame
		The parsed space weather data with the 30 min or 60 min index.
		The index is returned timezone-naive but contains UTC timestamps.
		To convert to a timezone-aware index, use
		:meth:`pandas.DataFrame.tz_localize()`: ``hp_df.tz_localize("utc")``.
		Raises an ``IOError`` if the file is not found.

		The dataframe contains the following columns:

		"index":
			padas.DateTimeIndex of the middle times of the intervals.
		"year", "month", "day":
			The observation date.
		"hh_h":
			Starting time in hours of interval.
		"hh_m":
			Middle time in hours of interval.
		"days":
			Days since 1932-01-01 00:00 UT to start of interval.
		"days_m":
			Days since 1932-01-01 00:00 UT to middle of interval.
		"Hp":
			Hp index during to the interval (30 min or 60 min).
		"ap":
			ap index during to the interval (30 min or 60 min).
		"D":
			Reserved for future use, D = 0 for now.
	"""
	_assert_file_exists(gfzhppath)
	hp = np.genfromtxt(
		gfzhppath,
		delimiter=[
		#  yy mm dd hh hm ddd ddm hp ap  D
			4, 3, 3, 5, 6, 12, 12, 7, 5, 2,
		],
		dtype=(
			"i4,i4,i4,f4,f4,f4,f4,f4,i4,i4"
		),
		names=[
			"year", "month", "day", "hh_h", "hh_m", "days", "days_m", "Hp", "ap", "D",
		]
	)
	hp = hp[hp["year"] != -1]
	ts = pd.to_datetime([
		"{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}".format(
			yy, mm, dd, int(np.floor(hh_m)), int(60 * (hh_m - np.floor(hh_m)))
		)
		for yy, mm, dd, hh_m in hp[["year", "month", "day", "hh_m"]]
	])
	hp_df = pd.DataFrame(hp, index=ts)
	return hp_df


def read_gfz_wdc(gfzpath):
	"""Parse space weather index data file in WDC format

	Parses the GFZ index data in WDC format.

	Parameters
	----------
	gfzpath: str
		File to parse, absolute path or relative to the current dir.

	Returns
	-------
	gfz_df: pandas.DataFrame
		The parsed space weather data (daily values).
		Raises an ``IOError`` if the file is not found.
		The index is returned timezone-naive but contains UTC timestamps.
		To convert to a timezone-aware index, use
		:meth:`pandas.DataFrame.tz_localize()`: ``gfz_df.tz_localize("utc")``.

		The dataframe contains the following columns:

		"year", "month", "day":
			The observation date
		"bsrn":
			Bartels Solar Rotation Number.
			A sequence of 27-day intervals counted continuously from 1832 Feb 8.
		"rotd":
			Number of Day within the Bartels 27-day cycle (01-27).
		"Kp0", "Kp3", "Kp6", "Kp9", "Kp12", "Kp15", "Kp18", "Kp21":
			Planetary 3-hour Range Index (Kp) for 0000-0300, 0300-0600,
			0600-0900, 0900-1200, 1200-1500, 1500-1800, 1800-2100, 2100-2400 UT
		"Kpsum": Sum of the 8 Kp indices for the day.
			Expressed to the nearest third of a unit.
		"Ap0", "Ap3", "Ap6", "Ap9", "Ap12", "Ap15", "Ap18", "Ap21":
			Planetary Equivalent Amplitude (Ap) for 0000-0300, 0300-0600,
			0600-0900, 0900-1200, 1200-1500, 1500-1800, 1800-2100, 2100-2400 UT
		"Apavg":
			Arithmetic average of the 8 Ap indices for the day.
		"Cp":
			Cp index - the daily planetary character figure, a qualitative
			estimate of the overall level of geomagnetic activity for this day
			determined from the sum of the eight ap amplitudes,
			ranging from 0.0 to 2.5 in steps of 0.1.
		"C9":
			The contracted scale for Cp with only 1 digit, from 0 to 9.
	"""
	_assert_file_exists(gfzpath)
	gfz = np.genfromtxt(
		gfzpath,
		skip_header=3,
		delimiter=[
		#  yy mm dd br db kp kp kp kp kp kp kp kp kps
			2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3,
		#  ap ap ap ap ap ap ap ap Ap Cp C9
			3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1,
		],
		dtype=(
			"i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,"
			"i4,i4,i4,i4,i4,i4,i4,i4,i4,f8,i4,"
		),
		names=[
			"year", "month", "day", "bsrn", "rotd",
			"Kp0", "Kp3", "Kp6", "Kp9", "Kp12", "Kp15", "Kp18", "Kp21", "Kpsum",
			"Ap0", "Ap3", "Ap6", "Ap9", "Ap12", "Ap15", "Ap18", "Ap21", "Apavg",
			"Cp", "C9",
		]
	)
	gfz = gfz[gfz["year"] != -1]
	ts = pd.to_datetime([
		"{0:04d}-{1:02d}-{2:02d}".format(2000 + yy if yy < 32 else 1900 + yy, mm, dd)
		for yy, mm, dd in gfz[["year", "month", "day"]]
	])
	gfz_df = pd.DataFrame(gfz, index=ts)
	gfz_df.loc[:, "year"] = ts.year
	# Adjust Kp to 0...9
	kpns = list(map("Kp{0}".format, range(0, 23, 3))) + ["Kpsum"]
	gfz_df[kpns] = 0.1 * gfz_df[kpns]
	return gfz_df


# Common arguments for the public daily and 3h interfaces
_GFZ_COMMON_PARAMS = """
Parameters
----------
gfzpath_all: str, optional, default depending on package install location
	Filename for the large combined index file including the
	historic data, absolute path or relative to the current dir.
gfzpath_30d: str, optional, default depending on package install location
	Filename for the 30-day (nowcast) index file,
	absolute path or relative to the current dir.
update: bool, optional, default False
	Attempt to update the local data if it is older than `update_interval`.
update_interval: str, optional, default "10days"
	The time after which the data are considered "old".
	By default, no automatic re-download is initiated, set `update` to true.
	The online data is updated every 3 hours, thus setting this value to
	a shorter time is not needed and not recommended.
gfz_format: str, optional, default `None`
	The file format to parse the files passed via `gfzpath_all` and `gfzpath_all`.
	Use `None`, "default", "gfz", or "standard" for the "standard" GFZ ASCII files.
	Use "wdc" to parse files in WDC format into a full-length `pandas.DataFrame`.
	Use "hp30" or "hp60" to read the Hp30 and Hp60 data files.
"""

_PARSERS = {
	"default": (read_gfz, update_gfz),
	"gfz": (read_gfz, update_gfz),
	"standard": (read_gfz, update_gfz),
	"wdc": (read_gfz_wdc, update_gfz),
	"hp30": (read_gfz_hp, update_gfz_hp30),
	"hp60": (read_gfz_hp, update_gfz_hp60),
}


def _doc_param(**sub):
	def dec(obj):
		obj.__doc__ = obj.__doc__.format(**sub)
		return obj
	return dec


@_doc_param(params=_GFZ_COMMON_PARAMS)
def gfz_daily(
	gfzpath_all=GFZ_PATH_ALL,
	gfzpath_30d=GFZ_PATH_30D,
	update=False,
	update_interval="10days",
	gfz_format=None,
):
	"""Combined daily Ap, Kp, and f10.7 index values

	Combines the "historic" and last-30-day data into one dataframe.

	All arguments are optional and changing them from the defaults should not
	be required neither should it be necessary nor is it recommended.
	{params}
	Returns
	-------
	gfz_df: pandas.DataFrame
		The combined parsed space weather data (daily values).
		Raises ``IOError`` if the data files cannot be found.
		The index is returned timezone-naive but contains UTC timestamps.
		To convert to a timezone-aware index, use
		:meth:`pandas.DataFrame.tz_localize()`: ``gfz_df.tz_localize("utc")``.

	See Also
	--------
	gfz_3h, read_gfz
	"""
	gfz_format = gfz_format or "gfz"
	parse_func, update_func = _PARSERS[gfz_format.lower()]
	# ensure that the file exists and is up to date
	if (
		not os.path.exists(gfzpath_all)
		or not os.path.exists(gfzpath_30d)
	):
		warn("Could not find space weather data, trying to download.")
		update_func(gfzpath_all=gfzpath_all, gfzpath_30d=gfzpath_30d)

	if (
		get_gfz_age(gfzpath_all) > pd.Timedelta("30days")
		or get_gfz_age(gfzpath_30d) > pd.Timedelta(update_interval)
	):
		if update:
			update_func(gfzpath_all=gfzpath_all, gfzpath_30d=gfzpath_30d)
		else:
			warn(
				"Local data files are older than {0}, pass `update=True` or "
				"run `gfz.update_gfz()` manually if you need newer data.".format(
					update_interval
				)
			)

	df_all = parse_func(gfzpath_all)
	df_30d = parse_func(gfzpath_30d)
	return pd.concat([df_all, df_30d[df_all.index[-1]:].iloc[1:]])


@_doc_param(params=_GFZ_COMMON_PARAMS)
def gfz_3h(*args, **kwargs):
	"""3h values of Ap and Kp

	Provides the 3-hourly Ap and Kp indices from the full daily data set.

	Accepts the same arguments as `gfz_daily()`.
	All arguments are optional and changing them from the defaults should not
	be required neither should it be necessary nor is it recommended.
	{params}
	Returns
	-------
	gfz_df: pandas.DataFrame
		The combined Ap and Kp index data (3h values).
		The index values are centred at the 3h interval, i.e. at 01:30:00,
		04:30:00, 07:30:00, ... and so on.
		Raises ``IOError`` if the data files cannot be found.
		The index is returned timezone-naive but contains UTC timestamps.
		To convert to a timezone-aware index, use
		:meth:`pandas.DataFrame.tz_localize()`: ``gfz_df.tz_localize("utc")``.

	See Also
	--------
	gfz_daily
	"""
	daily_df = gfz_daily(*args, **kwargs)
	ret = daily_df.copy()
	apns = list(map("Ap{0}".format, range(0, 23, 3)))
	kpns = list(map("Kp{0}".format, range(0, 23, 3)))
	for i, (ap, kp) in enumerate(zip(apns, kpns)):
		ret[ap].index = daily_df[ap].index + pd.Timedelta((i * 3 + 1.5), unit="h")
		ret[kp].index = daily_df[kp].index + pd.Timedelta((i * 3 + 1.5), unit="h")
	gfz_ap = pd.concat(map(ret.__getitem__, apns))
	gfz_kp = pd.concat(map(ret.__getitem__, kpns))
	df = pd.DataFrame({"Ap": gfz_ap, "Kp": gfz_kp})
	return df.reindex(df.index.sort_values())
