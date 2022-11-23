# Copyright (c) 2020--2022 Stefan Bender
#
# This module is part of pyspaceweather.
# pyspaceweather is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying COPYING.GPLv2 file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python interface for space weather indices

Celestrak space weather indices file parser for python [#]_.

.. [#] https://celestrak.com/SpaceData/
"""
import os
from pkg_resources import resource_filename
import logging
from warnings import warn

import numpy as np
import pandas as pd

from .core import _assert_file_exists, _dl_file

__all__ = [
	"sw_daily", "ap_kp_3h", "read_sw",
	"get_file_age", "update_data",
	"SW_PATH_ALL", "SW_PATH_5Y",
]

DL_URL_ALL = "https://celestrak.com/SpaceData/SW-All.txt"
DL_URL_5Y = "https://celestrak.com/SpaceData/SW-Last5Years.txt"
SW_FILE_ALL = os.path.basename(DL_URL_ALL)
SW_FILE_5Y = os.path.basename(DL_URL_5Y)
SW_PATH_ALL = resource_filename(__name__, os.path.join("data", SW_FILE_ALL))
SW_PATH_5Y = resource_filename(__name__, os.path.join("data", SW_FILE_5Y))


def get_file_age(swpath, relative=True):
	"""Age of the downloaded data file

	Retrieves the last update time of the given file or full path.

	Parameters
	----------
	swpath: str
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
	_assert_file_exists(swpath)
	with open(swpath) as fp:
		for line in fp:
			if line.startswith("UPDATED"):
				# closes the file automatically
				break
	upd = pd.to_datetime(line.lstrip("UPDATED"), utc=True)
	if relative:
		return pd.Timestamp.utcnow() - upd
	return upd


def update_data(
	min_age="3h",
	swpath_all=SW_PATH_ALL, swpath_5y=SW_PATH_5Y,
	url_all=DL_URL_ALL, url_5y=DL_URL_5Y,
):
	"""Update the local space weather index data

	Updates the local space weather index data from the website [#]_,
	given that the 5-year file is older
	than `min_age`, or the combined (large) file is older than four years.
	If the data is missing for some reason, a download will be attempted nonetheless.

	All arguments are optional and changing them from the defaults should not
	be required neither should it be necessary nor is it recommended.

	.. [#] https://celestrak.com/SpaceData/

	Parameters
	----------
	min_age: str, optional, default "3h"
		The time after which a new download will be attempted.
		The online data is updated every 3 hours, thus setting this value to
		a shorter time is not needed and not recommended.
	swpath_all: str, optional, default depending on package install location
		Filename for the large combined index file including the
		historic data, absolute path or relative to the current dir.
	swpath_5y: str, optional, default depending on package install location
		Filename for the 5-year index file, absolute path or relative to the current dir.
	url_all: str, optional, default `sw.DL_URL_ALL`
		The url of the "historic" data file.
	url_5y: str, optional, default `sw.DL_URL_5Y`
		The url of the data file of containing the indices of the last 5 years.

	Returns
	-------
	Nothing.
	"""
	def _update_file(swpath, url, min_age):
		if not os.path.exists(swpath):
			logging.info("{0} not found, downloading.".format(swpath))
			_dl_file(swpath, url)
			return
		if get_file_age(swpath) < pd.Timedelta(min_age):
			logging.info("not updating '{0}'.".format(swpath))
			return
		logging.info("updating '{0}'.".format(swpath))
		_dl_file(swpath, url)

	# Update the large file after four years
	# to have some overlap with the 5-year data
	# 1460 = 4 * 365
	_update_file(swpath_all, url_all, "1460days")
	# Don't re-download before `min_age` has passed (3h)
	_update_file(swpath_5y, url_5y, min_age)


def read_sw(swpath):
	"""Read and parse space weather index data file

	Reads the given file and parses it according to the space weather data format.

	Parameters
	----------
	swpath: str
		File to parse, absolute path or relative to the current dir.

	Returns
	-------
	sw_df: pandas.DataFrame
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
		"Cp":
			Cp or Planetary Daily Character Figure. A qualitative estimate of
			overall level of magnetic activity for the day determined from the sum
			of the 8 Ap indices. Cp ranges, in steps of one-tenth, from 0 (quiet)
			to 2.5 (highly disturbed). "C9":
		"isn":
			International Sunspot Number.
			Records contain the Zurich number through 1980 Dec 31 and the
			International Brussels number thereafter.
		"f107_adj":
			10.7-cm Solar Radio Flux (F10.7) Adjusted to 1 AU.
			Measured at Ottawa at 1700 UT daily from 1947 Feb 14 until
			1991 May 31 and measured at Penticton at 2000 UT from 1991 Jun 01 on.
			Expressed in units of 10-22 W/m2/Hz.
		"Q":
			Flux Qualifier.
			0 indicates flux required no adjustment;
			1 indicates flux required adjustment for burst in progress at time of measurement;
			2 indicates a flux approximated by either interpolation or extrapolation;
			3 indicates no observation; and
			4 indicates CSSI interpolation of missing data.
		"f107_81ctr_adj":
			Centered 81-day arithmetic average of F10.7 (adjusted).
		"f107_81lst_adj":
			Last 81-day arithmetic average of F10.7 (adjusted).
		"f107_obs":
			Observed (unadjusted) value of F10.7.
		"f107_81ctr_obs":
			Centered 81-day arithmetic average of F10.7 (observed).
		"f107_81lst_obs":
			Last 81-day arithmetic average of F10.7 (observed).
	"""
	_assert_file_exists(swpath)
	sw = np.genfromtxt(
		swpath,
		skip_header=3,
		delimiter=[
		#  yy mm dd br rd kp kp kp kp kp kp kp kp Kp
			4, 3, 3, 5, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4,
		#  ap ap ap ap ap ap ap ap Ap cp c9 is f1  q
			4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 2, 4, 6, 2,
		#  f2 f3 f4 f5 f6
			6, 6, 6, 6, 6],
		dtype=(
			"i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,"
			"i4,i4,i4,i4,i4,i4,i4,i4,i4,f8,i4,i4,f8,i4,"
			"f8,f8,f8,f8,f8"
		),
		names=[
			"year", "month", "day", "bsrn", "rotd",
			"Kp0", "Kp3", "Kp6", "Kp9", "Kp12", "Kp15", "Kp18", "Kp21", "Kpsum",
			"Ap0", "Ap3", "Ap6", "Ap9", "Ap12", "Ap15", "Ap18", "Ap21", "Apavg",
			"Cp", "C9", "isn", "f107_adj", "Q", "f107_81ctr_adj", "f107_81lst_adj",
			"f107_obs", "f107_81ctr_obs", "f107_81lst_obs"
		]
	)[2:-1]
	sw = sw[sw["year"] != -1]
	ts = pd.to_datetime([
		"{0:04d}-{1:02d}-{2:02d}".format(yy, mm, dd)
		for yy, mm, dd in sw[["year", "month", "day"]]
	])
	sw_df = pd.DataFrame(sw, index=ts)
	# Adjust Kp to 0...9
	kpns = list(map("Kp{0}".format, range(0, 23, 3))) + ["Kpsum"]
	sw_df[kpns] = 0.1 * sw_df[kpns]
	return sw_df


# Common arguments for the public daily and 3h interfaces
_SW_COMMON_PARAMS = """
	Parameters
	----------
	swpath_all: str, optional, default depending on package install location
		Filename for the large combined index file including the
		historic data, absolute path or relative to the current dir.
	swpath_5y: str, optional, default depending on package install location
		Filename for the 5-year index file, absolute path or relative to the current dir.
	update: bool, optional, default False
		Attempt to update the local data if it is older than `update_interval`.
	update_interval: str, optional, default "30days"
		The time after which the data are considered "old".
		By default, no automatic re-download is initiated, set `update` to true.
		The online data is updated every 3 hours, thus setting this value to
		a shorter time is not needed and not recommended.
"""


def _doc_param(**sub):
	def dec(obj):
		obj.__doc__ = obj.__doc__.format(**sub)
		return obj
	return dec


@_doc_param(params=_SW_COMMON_PARAMS)
def sw_daily(swpath_all=SW_PATH_ALL, swpath_5y=SW_PATH_5Y, update=False, update_interval="30days"):
	"""Combined daily Ap, Kp, and f10.7 index values

	Combines the "historic" and last-5-year data into one dataframe.

	All arguments are optional and changing them from the defaults should not
	be required neither should it be necessary nor is it recommended.
	{params}
	Returns
	-------
	sw_df: pandas.DataFrame
		The combined parsed space weather data (daily values).
		Raises ``IOError`` if the data files cannot be found.

	See Also
	--------
	ap_kp_3h, read_sw
	"""
	# ensure that the file exists and is up to date
	if (
		not os.path.exists(swpath_all)
		or not os.path.exists(swpath_5y)
	):
		warn("Could not find space weather data, trying to download.")
		update_data(swpath_all=swpath_all, swpath_5y=swpath_5y)

	if (
		# 1460 = 4 * 365
		get_file_age(swpath_all) > pd.Timedelta("1460days")
		or get_file_age(swpath_5y) > pd.Timedelta(update_interval)
	):
		if update:
			update_data(swpath_all=swpath_all, swpath_5y=swpath_5y)
		else:
			warn(
				"Local data files are older than {0}, pass `update=True` or "
				"run `sw.update_data()` manually if you need newer data.".format(
					update_interval
				)
			)

	df_all = read_sw(swpath_all)
	df_5y = read_sw(swpath_5y)
	return pd.concat([df_all[:df_5y.index[0]], df_5y[1:]])


@_doc_param(params=_SW_COMMON_PARAMS)
def ap_kp_3h(*args, **kwargs):
	"""3h values of Ap and Kp

	Provides the 3-hourly Ap and Kp indices from the full daily data set.

	Accepts the same arguments as `sw_daily()`.
	All arguments are optional and changing them from the defaults should not
	be required neither should it be necessary nor is it recommended.
	{params}
	Returns
	-------
	sw_df: pandas.DataFrame
		The combined Ap and Kp index data (3h values).
		The index values are centred at the 3h interval, i.e. at 01:30:00,
		04:30:00, 07:30:00, ... and so on.
		Raises ``IOError`` if the data files cannot be found.

	See Also
	--------
	sw_daily
	"""
	daily_df = sw_daily(*args, **kwargs)
	ret = daily_df.copy()
	apns = list(map("Ap{0}".format, range(0, 23, 3)))
	kpns = list(map("Kp{0}".format, range(0, 23, 3)))
	for i, (ap, kp) in enumerate(zip(apns, kpns)):
		ret[ap].index = daily_df[ap].index + pd.Timedelta((i * 3 + 1.5), unit="h")
		ret[kp].index = daily_df[kp].index + pd.Timedelta((i * 3 + 1.5), unit="h")
	sw_ap = pd.concat(map(ret.__getitem__, apns))
	sw_kp = pd.concat(map(ret.__getitem__, kpns))
	df = pd.DataFrame({"Ap": sw_ap, "Kp": sw_kp})
	return df.reindex(df.index.sort_values())
