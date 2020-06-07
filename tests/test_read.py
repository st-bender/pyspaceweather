# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
#
# Copyright (c) 2020 Stefan Bender
#
# This module is part of pyspaceweather.
# pyspaceweather is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying COPYING.GPLv2 file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Space weather index read tests
"""
import numpy as np
import pandas as pd

from spaceweather import ap_kp_3h, sw_daily


def test_update():
	import os
	from pkg_resources import resource_filename
	from spaceweather.core import check_for_update, _get_last_update, SW_FILE
	swpath = resource_filename("spaceweather", os.path.join("data", SW_FILE))
	fdate = _get_last_update(swpath)
	now = pd.Timestamp.utcnow()
	assert (now - fdate > pd.Timedelta("1d")) == check_for_update(swpath, max_age="1d")


def test_daily():
	df = sw_daily()
	np.testing.assert_allclose(
		df.loc["2000-01-01"].values,
		np.array([
			2.000e+03, 1.000e+00, 1.000e+00, 2.272e+03, 7.000e+00, 5.300e+00, 4.700e+00,
			4.000e+00, 3.300e+00, 4.300e+00, 3.000e+00, 4.300e+00, 3.700e+00, 3.270e+01,
			5.600e+01, 3.900e+01, 2.700e+01, 1.800e+01, 3.200e+01, 1.500e+01, 3.200e+01,
			2.200e+01, 3.000e+01, 1.300e+00, 6.000e+00, 4.800e+01, 1.256e+02, 0.000e+00,
			1.605e+02, 1.750e+02, 1.299e+02, 1.656e+02, 1.790e+02,
		]),
		rtol=1e-12,
	)


def test_3hourly_ap():
	df = ap_kp_3h()
	np.testing.assert_allclose(
		df.loc[pd.date_range("2000-01-01 01:30", "2000-01-01 23:30", freq='3h')].Ap.values,
		np.array([56, 39, 27, 18, 32, 15, 32, 22]),
		rtol=1e-12,
	)


def test_3hourly_kp():
	df = ap_kp_3h()
	np.testing.assert_allclose(
		df.loc[pd.date_range("2000-01-01 01:30", "2000-01-01 23:30", freq='3h')].Kp.values,
		np.array([5.3, 4.7, 4.0, 3.3, 4.3, 3.0, 4.3, 3.7]),
		rtol=1e-12,
	)
