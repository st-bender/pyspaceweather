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
import os

import numpy as np
import pandas as pd
import requests

import pytest

from spaceweather import (
	ap_kp_3h, sw_daily, get_file_age, update_data,
	SW_PATH_ALL, SW_PATH_5Y,
)
from spaceweather.celestrak import DL_URL_5Y


@pytest.fixture(scope="module")
def df_3h():
	return ap_kp_3h()


def test_age():
	now = pd.Timestamp.utcnow()
	for p in [SW_PATH_ALL, SW_PATH_5Y]:
		assert os.path.exists(p)
		fage0 = get_file_age(p)
		fage1 = now - get_file_age(p, relative=False)
		assert (fage0 > pd.Timedelta("3h")) == (fage1 > pd.Timedelta("3h"))
		assert (fage0 > pd.Timedelta("1d")) == (fage1 > pd.Timedelta("1d"))


def _assert_age(p, age):
	assert os.path.exists(p)
	fage = get_file_age(p)
	assert fage < pd.Timedelta(age)


def test_update():
	update_data(min_age="100d")
	for (p, age) in zip([SW_PATH_ALL, SW_PATH_5Y], ["1460d", "100d"]):
		_assert_age(p, age)


def test_auto_update(mocker, tmpdir):
	# test with non-existent file
	mocker.patch("requests.get")
	tmpdir = str(tmpdir)
	update_data(swpath_5y=os.path.join(tmpdir, "foo.dat"))
	requests.get.assert_called_with(DL_URL_5Y, stream=True)
	# Should update the last-5-year data
	sw_daily(update=True, update_interval="1d")
	requests.get.assert_called_with(DL_URL_5Y, stream=True)
	_assert_age(SW_PATH_5Y, "100d")
	with pytest.warns(UserWarning):
		sw_daily(update=False, update_interval="0h")


def test_not_avail(mocker, tmpdir):
	# test with non-existent file
	mocker.patch("requests.get")
	tmpdir = str(tmpdir)
	tmpfile = os.path.join(tmpdir, "foo.dat")
	# daily
	with pytest.raises(IOError):
		with pytest.warns(UserWarning):
			sw_daily(update=False, update_interval="0h", swpath_5y=tmpfile)
	# 3h data
	with pytest.raises(IOError):
		with pytest.warns(UserWarning):
			ap_kp_3h(update=False, update_interval="0h", swpath_5y=tmpfile)


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


@pytest.mark.parametrize(
	"name, result",
	[
		("Ap", np.array([56, 39, 27, 18, 32, 15, 32, 22])),
		("Kp", np.array([5.3, 4.7, 4.0, 3.3, 4.3, 3.0, 4.3, 3.7])),
	]
)
def test_3hourly_index(name, result, df_3h):
	df = df_3h
	np.testing.assert_allclose(
		df.loc[
			pd.date_range(
				"2000-01-01 01:30", "2000-01-01 23:30", freq="3h"
			)
		][name].values,
		result,
		rtol=1e-12,
	)
