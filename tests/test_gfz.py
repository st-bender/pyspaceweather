# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
#
# Copyright (c) 2024 Stefan Bender
#
# This module is part of pyspaceweather.
# pyspaceweather is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying COPYING.GPLv2 file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Space weather index read tests for GFZ formats

Parsing tests for the GFZ file formats.
"""
import os

import numpy as np
import pandas as pd
import requests

import pytest

from spaceweather import (
	gfz_3h, gfz_daily, get_gfz_age, update_gfz,
)
from spaceweather.gfz import GFZ_URL_30D, HP30_URL_30D, HP60_URL_30D

GFZ_PATH_ALL = os.path.join("tests", "Kp_ap_Ap_SN_F107_since_2024.txt")
GFZ_PATH_30D = os.path.join("tests", "Kp_ap_Ap_SN_F107_nowcast.txt")

HP30_PATH_ALL = os.path.join("tests", "Hp30_ap30_complete_series.txt")
HP30_PATH_30D = os.path.join("tests", "Hp30_ap30_nowcast.txt")

HP60_PATH_ALL = os.path.join("tests", "Hp60_ap60_complete_series.txt")
HP60_PATH_30D = os.path.join("tests", "Hp60_ap60_nowcast.txt")


@pytest.fixture(scope="module")
def df_3h():
	return gfz_3h(gfzpath_all=GFZ_PATH_ALL, gfzpath_30d=GFZ_PATH_30D)


def test_age():
	now = pd.Timestamp.utcnow()
	for p in [GFZ_PATH_ALL, GFZ_PATH_30D]:
		assert os.path.exists(p)
		fage0 = get_gfz_age(p)
		fage1 = now - get_gfz_age(p, relative=False)
		assert (fage0 > pd.Timedelta("3h")) == (fage1 > pd.Timedelta("3h"))
		assert (fage0 > pd.Timedelta("1d")) == (fage1 > pd.Timedelta("1d"))


def test_update(mocker):
	mocker.patch("requests.get")
	update_gfz(min_age="1d", gfzpath_all=GFZ_PATH_ALL, gfzpath_30d=GFZ_PATH_30D)
	requests.get.assert_called_with(GFZ_URL_30D, stream=True)


def test_auto_update(mocker, tmpdir):
	# test with non-existent file
	mocker.patch("requests.get")
	tmpdir = str(tmpdir)
	update_gfz(gfzpath_30d=os.path.join(tmpdir, "foo.dat"))
	requests.get.assert_called_with(GFZ_URL_30D, stream=True)
	# Should update the last-5-year data
	gfz_daily(
		gfzpath_all=GFZ_PATH_ALL, gfzpath_30d=GFZ_PATH_30D,
		update=True, update_interval="1d",
	)
	requests.get.assert_called_with(GFZ_URL_30D, stream=True)
	with pytest.warns(UserWarning):
		gfz_daily(
			gfzpath_all=GFZ_PATH_ALL, gfzpath_30d=GFZ_PATH_30D,
			update=False, update_interval="0h",
		)


def test_not_avail(mocker, tmpdir):
	# test with non-existent file
	mocker.patch("requests.get")
	tmpdir = str(tmpdir)
	tmpfile = os.path.join(tmpdir, "foo.dat")
	# daily
	with pytest.raises(IOError):
		with pytest.warns(UserWarning):
			gfz_daily(update=False, update_interval="0h", gfzpath_30d=tmpfile)
	# 3h data
	with pytest.raises(IOError):
		with pytest.warns(UserWarning):
			gfz_3h(update=False, update_interval="0h", gfzpath_30d=tmpfile)


def test_daily():
	df = gfz_daily(gfzpath_all=GFZ_PATH_ALL, gfzpath_30d=GFZ_PATH_30D)
	np.testing.assert_allclose(
		df.loc["2024-01-01"].values,
		np.array([
			2.024e+03, 1.000e+00, 1.000e+00,
			3.36030e+04, 3.36035e+04, 2.596e+03, 2.500e+01,
			6.670e-01, 3.330e-01, 6.670e-01, 1.333e+00,
			2.000e+00, 3.000e+00, 3.333e+00, 4.000e+00, 1.5333e+01,
			3.000e+00, 2.000e+00, 3.000e+00, 5.000e+00,
			7.000e+00, 1.500e+01, 1.800e+01, 2.700e+01, 1.000e+01,
			5.400e+01, 1.357e+02, 1.312e+02, 1.000e+00,
		], dtype=np.float64),
		rtol=1e-6,
	)


@pytest.mark.parametrize(
	"name, result",
	[
		("Ap", [3, 2, 3, 5, 7, 15, 18, 27]),
		("Kp", [0.667, 0.333, 0.667, 1.333, 2.0, 3.0, 3.333, 4.0]),
	]
)
def test_3hourly_index(name, result, df_3h):
	df = df_3h
	np.testing.assert_allclose(
		df.loc[
			pd.date_range(
				"2024-01-01 01:30", "2024-01-01 23:30", freq="3h"
			)
		][name].values,
		np.array(result, dtype=np.float64),
		rtol=1e-6,
	)


@pytest.mark.parametrize(
	"fpall, fp30d, url",
	[
		(HP30_PATH_ALL, HP30_PATH_30D, HP30_URL_30D),
		(HP60_PATH_ALL, HP60_PATH_30D, HP60_URL_30D),
	],
	ids=["Hp30", "Hp60"],
)
def test_auto_update_hp(fpall, fp30d, url, mocker, request):
	mocker.patch("requests.get")
	_gfz_fmt = request.node.callspec.id.lower()
	# Should update the last-5-year data
	gfz_daily(
		gfzpath_all=fpall, gfzpath_30d=fp30d,
		update=True, update_interval="1d",
		gfz_format=_gfz_fmt,
	)
	requests.get.assert_called_with(url, stream=True)


@pytest.mark.parametrize(
	"fpall, fp30d, index, expected",
	[
		(
			HP30_PATH_ALL, HP30_PATH_30D, "2025-07-01 00:15",
			[2025, 7, 1, 0, 0.25, 34150.0, 34150.01042, 3.000, 15, 0],
		),
		(
			HP60_PATH_ALL, HP60_PATH_30D, "2025-07-01 00:30",
			[2025, 7, 1, 0, 0.50, 34150.0, 34150.02083, 3.333, 18, 0],
		),
	],
	ids=["Hp30", "Hp60"],
)
def test_daily_hp(fpall, fp30d, index, expected, request):
	_gfz_fmt = request.node.callspec.id.lower()
	df = gfz_daily(
		gfzpath_all=fpall,
		gfzpath_30d=fp30d,
		gfz_format=_gfz_fmt,
	)
	np.testing.assert_allclose(
		df.loc[index].values,
		np.array(expected, dtype=np.float64),
		rtol=1e-6,
	)
