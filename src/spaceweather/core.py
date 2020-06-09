# Copyright (c) 2020 Stefan Bender
#
# This module is part of pyspaceweather.
# pyspaceweather is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying COPYING.GPLv2 file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python interface for space weather indices

"""
import os
from pkg_resources import resource_filename
import requests
import logging
from warnings import warn

import numpy as np
import pandas as pd

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


def _dl_file(swpath, url=DL_URL_ALL):
	with requests.get(url, stream=True) as r:
		with open(swpath, 'wb') as fd:
			for chunk in r.iter_content(chunk_size=1024):
				fd.write(chunk)


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
	upd: pd.Timestamp or pd.Timedelta
		The last updated time or the file age, depending on the setting
		of `relative` above.
	"""
	for line in open(swpath):
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

	Updates the local space weather index data from the website
	<https://celestrak.com/SpaceData/>, given that the 5-year file is older
	than `min_age`, or the combined (large) file is older than four years.
	If the data is missing for some reason, a download will be attempted nonetheless.

	All arguments are optional and changing them from the defaults should not
	be required neither should it be necessary nor is it recommended.

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
	sw_df: pd.Dataframe
		The parsed space weather data (daily values).
	"""
	kpns = ["Kp{0}".format(i) for i in range(0, 23, 3)] + ["Kpsum"]
	sw = np.genfromtxt(
		swpath,
		skip_header=3,
				# yy mm dd br rd kp kp kp kp kp kp kp kp Kp ap ap ap ap ap ap ap ap Ap cp c9 is f1  q f2 f3 f4 f5 f6
		delimiter=[4, 3, 3, 5, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 2, 4, 6, 2, 6, 6, 6, 6, 6],
		dtype=   "i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,i4,f8,i4,i4,f8,i4,f8,f8,f8,f8,f8",
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
	sw_df: pd.Dataframe
		The combined parsed space weather data (daily values).
	"""
	# ensure that the file exists and is up to date
	if (
		not os.path.exists(swpath_all)
		or not os.path.exists(swpath_5y)
	):
		warn("Could not find space weather data, trying to download.")
		update_data()

	if (
		# 1460 = 4 * 365
		get_file_age(swpath_all) > pd.Timedelta("1460days")
		or get_file_age(swpath_5y) > pd.Timedelta(update_interval)
	):
		if update:
			update_data()
		else:
			warn("Data files *might* be too old, consider running `sw.update_data()`.")

	df_all = read_sw(swpath_all)
	df_5y = read_sw(swpath_5y)
	return pd.concat([df_all[:df_5y.index[0]], df_5y[1:]])


@_doc_param(params=_SW_COMMON_PARAMS)
def ap_kp_3h(*args, **kwargs):
	"""Extract 3h values of Ap and Kp

	Extracts 3-hourly Ap and Kp indices from the full daily data set.

	Accepts the same arguments as `sw_daily()`.
	All arguments are optional and changing them from the defaults should not
	be required neither should it be necessary nor is it recommended.
	{params}
	Returns
	-------
	sw_df: pd.Dataframe
		The combined Ap and Kp index data (3h values).

	See Also
	--------
	`sw_daily()`
	"""
	daily_df = sw_daily(*args, **kwargs)
	ret = daily_df.copy()
	apns = ["Ap{0}".format(i) for i in range(0, 23, 3)]
	kpns = ["Kp{0}".format(i) for i in range(0, 23, 3)]
	for i, (ap, kp) in enumerate(zip(apns, kpns)):
		ret[ap].index = daily_df[ap].index + pd.Timedelta((i * 3 + 1.5), unit="h")
		ret[kp].index = daily_df[kp].index + pd.Timedelta((i * 3 + 1.5), unit="h")
	sw_ap = pd.concat([ret[ap] for ap in apns])
	sw_kp = pd.concat([ret[kp] for kp in kpns])
	return pd.DataFrame({"Ap": sw_ap, "Kp": sw_kp})
