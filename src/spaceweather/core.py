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


def sw_daily(swpath_all=SW_PATH_ALL, swpath_5y=SW_PATH_5Y, update=False, update_interval="30days"):
	"""Combined daily Ap, Kp, and f10.7 index values
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


def ap_kp_3h(swpath_all=SW_PATH_ALL, swpath_5y=SW_PATH_5Y, update=False, update_interval="30days"):
	"""Extract 3h values of Ap and Kp
	"""
	daily_df = sw_daily(
		swpath_all=swpath_all, swpath_5y=swpath_5y,
		update=update, update_interval=update_interval
	)
	ret = daily_df.copy()
	apns = ["Ap{0}".format(i) for i in range(0, 23, 3)]
	kpns = ["Kp{0}".format(i) for i in range(0, 23, 3)]
	for i, (ap, kp) in enumerate(zip(apns, kpns)):
		ret[ap].index = daily_df[ap].index + pd.Timedelta((i * 3 + 1.5), unit="h")
		ret[kp].index = daily_df[kp].index + pd.Timedelta((i * 3 + 1.5), unit="h")
	sw_ap = pd.concat([ret[ap] for ap in apns])
	sw_kp = pd.concat([ret[kp] for kp in kpns])
	return pd.DataFrame({"Ap": sw_ap, "Kp": sw_kp})
