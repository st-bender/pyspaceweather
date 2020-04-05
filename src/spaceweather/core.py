# Copyright (c) 2020 Stefan Bender
#
# This module is part of pyspaceweather.
# pynrlmsise00 is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying LICENSE file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python interface for space weather indices

"""
import os
from pkg_resources import resource_filename
import requests

import numpy as np
import pandas as pd

__all__ = ["sw_daily", "ap_kp_3h"]

DL_URL = "https://celestrak.com/SpaceData/SW-All.txt"
SW_FILE = "SW-All.txt"


def _dl_file(swfile):
	with requests.get(DL_URL, stream=True) as r:
		with open(swfile, 'wb') as fd:
			for chunk in r.iter_content(chunk_size=1024):
				fd.write(chunk)


def _read_sw(swpath):
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


def sw_daily(swfile=SW_FILE):
	"""Daily Ap, Kp, and f10.7 index values
	"""
	# ensure the file exists
	swpath = resource_filename("spaceweather", os.path.join("data", swfile))
	if not os.path.exists(swpath):
		_dl_file(swpath)
	return _read_sw(swpath)


def ap_kp_3h(swfile=SW_FILE):
	"""3h Ap and Kp index values
	"""
	daily_df = sw_daily(swfile)
	ret = daily_df.copy()
	apns = ["Ap{0}".format(i) for i in range(0, 23, 3)]
	kpns = ["Kp{0}".format(i) for i in range(0, 23, 3)]
	for i, (ap, kp) in enumerate(zip(apns, kpns)):
		ret[ap].index = daily_df[ap].index + pd.Timedelta((i * 3 + 1.5), unit="h")
		ret[kp].index = daily_df[kp].index + pd.Timedelta((i * 3 + 1.5), unit="h")
	sw_ap = pd.concat([ret[ap] for ap in apns])
	sw_kp = pd.concat([ret[kp] for kp in kpns])
	return pd.DataFrame({"Ap": sw_ap, "Kp": sw_kp})
