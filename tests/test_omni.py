# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
#
# Copyright (c) 2022 Stefan Bender
#
# This module is part of pyspaceweather.
# pyspaceweather is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying COPYING.GPLv2 file or http://www.gnu.org/licenses/gpl-2.0.html.
"""OMNI data read tests
"""
import os
import requests

import numpy as np
import pandas as pd

import pytest

from spaceweather import cache_omnie, omnie_hourly, omnie_mask_missing, sw_daily
from spaceweather.omni import OMNI_URL_BASE, OMNI_PREFIX, OMNI_EXT

_TEST_YEAR = 2012
_TEST_FILE = "{0}_{1:04d}.{2}".format(OMNI_PREFIX, _TEST_YEAR, OMNI_EXT)
_TEST_URL = os.path.join(OMNI_URL_BASE, _TEST_FILE)
_TEST_PATH = os.path.join(".", "tests")


@pytest.fixture(scope="module")
def df_d():
	return sw_daily()


@pytest.fixture(scope="module")
def df_o():
	return omnie_hourly(2000, local_path=_TEST_PATH, prefix="omni2t")


def test_cache(mocker, tmpdir):
	mocker.patch("requests.get")
	tmpdir = str(tmpdir)
	# Check non-existent file
	cache_omnie(year=_TEST_YEAR, local_path=tmpdir)
	requests.get.assert_called_once_with(_TEST_URL, stream=True)
	# Check non-existent (sub)dir
	tmppath = os.path.join(tmpdir, "data")
	cache_omnie(year=_TEST_YEAR, local_path=tmppath)
	requests.get.assert_called_with(_TEST_URL, stream=True)


def test_auto_update(mocker, tmpdir):
	# test with non-existent file
	mocker.patch("requests.get")
	tmpdir = str(tmpdir)
	with pytest.raises(IOError):
		with pytest.warns(UserWarning):
			omnie_hourly(year=_TEST_YEAR, cache=True, local_path=tmpdir)
	requests.get.assert_called_once_with(_TEST_URL, stream=True)


def test_not_avail(mocker, tmpdir):
	# test with non-existent file
	tmpdir = str(tmpdir)
	with pytest.raises(IOError):
		with pytest.warns(UserWarning):
			omnie_hourly(year=_TEST_YEAR, cache=False, local_path=tmpdir)


@pytest.mark.parametrize("hour", range(0, 24, 3))
@pytest.mark.parametrize("index", ["Ap", "Kp"])
def test_hourly(hour, index, df_d, df_o):
	df1 = df_o
	# The last row is for the missing value test.
	df1 = df1.iloc[:-1]
	df2 = df_d
	ind_name = "{0}{1}".format(index, hour)
	df1_ind = df1[df1["hour"] == hour][index]
	df2_ind = df2[ind_name].loc[df1_ind.index.date].rename(index)
	df2_ind.index = df1_ind.index
	pd.testing.assert_series_equal(df1_ind, df2_ind)


@pytest.mark.parametrize(
	"name, result",
	[
		("Ap", np.array([56, 39, 27, 18, 32, 15, 32, 22])),
		("Kp", np.array([5.3, 4.7, 4.0, 3.3, 4.3, 3.0, 4.3, 3.7])),
	]
)
def test_3hourly_index(name, result, df_o):
	df = df_o
	np.testing.assert_allclose(
		df.loc[
			pd.date_range(
				"2000-01-01 00:00", "2000-01-01 23:00", freq="3h"
			)
		][name].values,
		result,
		rtol=1e-12,
	)


def test_mask_missing(df_o):
	df = df_o
	dfp = omnie_mask_missing(df)
	# The last row should contain all NaNs.
	dfp = dfp.iloc[-1]
	for v in filter(
		lambda n: n not in ["year", "doy", "hour"],
		dfp.index,
	):
		assert np.isnan(dfp[v])
