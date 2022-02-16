# -*- coding: utf-8 -*-
# Copyright (c) 2022 Stefan Bender
#
# This module is part of pyspaceweather.
# pyspaceweather is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying COPYING.GPLv2 file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python interface for OMNI space weather data

Omni2 [#]_ space weather data interface for python.

.. [#] https://omniweb.gsfc.nasa.gov/ow.html
"""
import os
from pkg_resources import resource_filename
import logging
from warnings import warn

import numpy as np
import pandas as pd

from .core import _assert_file_exists, _dl_file

__all__ = [
	"cache_omnie",
	"omnie_hourly",
	"omnie_mask_missing",
	"read_omnie",
]

OMNI_URL_BASE = "https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/extended"
OMNI_PREFIX, OMNI_EXT = "omni2", "dat"
OMNI_SUBDIR = "omni_extended"
LOCAL_PATH = resource_filename(__name__, os.path.join("data", OMNI_SUBDIR))

_OMNI_MISSING = {
	"year": None,
	"doy": None,
	"hour": None,
	"bsrn": 9999,
	"id_imf": 99,
	"id_sw": 99,
	"n_imf": 999,
	"n_plasma": 999,
	"B_mag_avg": 999.9,
	"B_mag": 999.9,
	"theta_B": 999.9,
	"phi_B": 999.9,
	"B_x": 999.9,
	"B_y_GSE": 999.9,
	"B_z_GSE": 999.9,
	"B_y_GSM": 999.9,
	"B_z_GSM": 999.9,
	"sigma_B_mag_avg": 999.9,
	"sigma_B_mag": 999.9,
	"sigma_B_x_GSE": 999.9,
	"sigma_B_y_GSE": 999.9,
	"sigma_B_z_GSE": 999.9,
	"T_p": 9999999.0,
	"n_p": 999.9,
	"v_plasma": 9999.0,
	"phi_v": 999.9,
	"theta_v": 999.9,
	"n_alpha_n_p": 9.999,
	"p_flow": 99.99,
	"sigma_T": 9999999.0,
	"sigma_n": 999.9,
	"sigma_v": 9999.0,
	"sigma_phi_v": 999.9,
	"sigma_theta_v": 999.9,
	"sigma_na_np": 9.999,
	"E": 999.99,
	"beta_plasma": 999.99,
	"mach": 999.9,
	"Kp": 9.9,
	"R": 999,
	"Dst": 99999,
	"AE": 9999,
	"p_01MeV": 999999.99,
	"p_02MeV": 99999.99,
	"p_04MeV": 99999.99,
	"p_10MeV": 99999.99,
	"p_30MeV": 99999.99,
	"p_60MeV": 99999.99,
	"flag": 0,
	"Ap": 999,
	"f107_adj": 999.9,
	"PC": 999.9,
	"AL": 99999,
	"AU": 99999,
	"mach_mag": 99.9,
	"Lya": 0.999999,
	"QI_p": 9.9999
}


def cache_omnie(
	year,
	prefix=None,
	ext=None,
	local_path=None,
	url_base=None,
):
	"""Download OMNI2 data to local cache

	Downloads the OMNI2 (extended) data file from [#]_ to the local location.

	.. [#] https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/extended/

	Parameters
	----------
	year: int
		Year of the data.
	prefix: str, optional
		File prefix for constructing the file name as <prefix>_year.<ext>.
		Defaults to 'omni2'.
	ext: str, optional
		File extension for constructing the file name as <prefix>_year.<ext>.
		Defaults to 'dat'.
	local_path: str, optional
		Path to the locally stored data yearly files, defaults to the
		data location within the package.
	url_base: str, optional
		URL for the directory that contains the yearly files.

	Returns
	-------
	Nothing.
	"""
	prefix = prefix or OMNI_PREFIX
	ext = ext or OMNI_EXT
	local_path = local_path or LOCAL_PATH
	url_base = url_base or OMNI_URL_BASE

	basename = "{0}_{1:04d}.{2}".format(prefix, year, ext)

	if not os.path.exists(local_path):
		os.makedirs(local_path)

	omnie_file = os.path.join(local_path, basename)
	if not os.path.exists(omnie_file):
		url = os.path.join(url_base, basename)
		logging.info("%s not found, downloading from %s.", omnie_file, url)
		_dl_file(omnie_file, url)


def omnie_mask_missing(df):
	"""Mask missing values with NaN

	Marks missing values in the OMNI2 data set by NaN.
	The missing value indicating numbers are taken from the file format description
	https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/extended/aareadme_extended

	Parameters
	----------
	df: pandas.DataFrame
		The OMNI2 data set, e.g. from ``omnie_hourly()`` or ``read_omnie()``.

	Returns
	-------
	df: pandas.DataFrame
		The same dataframe with the missing values masked with numpy.nan.

	Note
	----
	This function returns a copy of the dataframe, and all the integer columns
	will be converted to float to support NaN.
	"""
	res = df.copy()
	for _c in df.columns:
		_m = _OMNI_MISSING.get(_c, None)
		if _m is None:
			continue
		_mask = df[_c] != _m
		res[_c] = df[_c].where(_mask)
	return res


def read_omnie(omnie_file):
	"""Read and parse OMNI2 extended files [#]_

	Parses the Omni2 extended data files,  available at [#]_,
	into a :class:`pandas.DataFrame`.

	.. [#] https://omniweb.gsfc.nasa.gov/ow.html
	.. [#] https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/extended/

	Parameters
	----------
	omnie_file: str
		File to parse, absolute path or relative to the current dir.

	Returns
	-------
	sw_df: pandas.DataFrame
		The parsed OMNI2 space weather data (hourly values).
		Details in
		https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/extended/aareadme_extended

		Raises an ``IOError`` if the file is not found.

		The dataframe contains the following columns:

		year:
			The observation year
		doy:
			Day of the year
		hour:
			Hour of the day
		bsrn:
			Bartels Solar Rotation Number.
		id_imf:
			ID for IMF spacecraft
		id_sw:
			ID for SW plasma spacecraft
		n_imf:
			Number of points in IMF averages
		n_plasma:
			Numberof points in plasma averages
		B_mag_avg:
			Magnetic field magnitude average B
		B_mag:
			Magnetic field vector magnitude
		theta_B:
			Latitude angle of the magnetic field vector
		phi_B:
			Longitude angle of the magnetic field vector
		B_x:
			B_x GSE, GSM
		B_y_GSE:
			B_y GSE
		B_z_GSE:
			B_z GSE
		B_y_GSM:
			B_y GSM
		B_z_GSM:
			B_z GSM
		sigma_B_mag_avg:
			RMS standard deviation of B_mag_avg
		sigma_B_mag:
			RMS standard deviation of B_mag
		sigma_B_x_GSE:
			RMS standard deviation of B_x_GSE
		sigma_B_y_GSE:
			RMS standard deviation of B_y_GSE
		sigma_B_z_GSE:
			RMS standard deviation of B_z_GSE
		T_p:
			Proton temperature
		n_p:
			Proton density
		v_plasma:
			Plasma flow speed
		phi_v:
			Plasma flow longitude angle
		theta_v:
			Plasma flow latitude angle
		n_alpha_n_p:
			Alpha/Proton ratio
		p_flow:
			Flow pressure
		sigma_T:
			Standard deviation of T_p
		sigma_n:
			Standard deviation of n_p
		sigma_v:
			Standard deviation of v_plasma
		sigma_phi_v:
			Standard deviation of phi_v
		sigma_theta_v:
			Standard deviation of theta_v
		sigma_na_np:
			Standard deviation of n_alpha_n_p
		E:
			Electric field magnitude
		beta_plasma:
			Plasma beta
		mach:
			Alfvén Mach number
		Kp:
			Kp index value
		R:
			Sunspot number
		Dst:
			Dst index value
		AE:
			AE index value
		p_01MeV, p_02MeV, p_04MeV, p_10MeV, p_30MeV, p_60MeV:
			Proton fluxes >1 MeV, >2 MeV, >4 MeV, >10 MeV, >30 MeV, > 60 MeV
		flag:
			Flag (-1, ..., 6)
		Ap:
			Ap index value
		f107_adj:
			F10.7 radio flux at 1 AU
		PC:
			PC index value
		AL, AU:
			AL and AU index values
		mach_mag:
			Magnetosonic Mach number

		The extended dataset contains the addional columns:

		Lya:
			Solar Lyman-alpha irradiance
		QI_p:
			Proton QI
	"""
	_assert_file_exists(omnie_file)
	# FORMAT(
	#     2I4,I3,I5,2I3,2I4,14F6.1,F9.0,F6.1,F6.0,2F6.1,F6.3,F6.2,
	#     F9.0,F6.1,F6.0,2F6.1,F6.3,2F7.2,F6.1,I3,I4,I6,I5,F10.2,
	#     5F9.2,I3,I4,2F6.1,2I6,F5.1,F9.6,F7.4
	# )
	sw = np.genfromtxt(
		omnie_file,
		skip_header=0,
		delimiter=[
		#   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
		#  yy dd hr br i1 i2 n1 n2  B B' tB fB Bx By Bz By Bz sB sB sB
			4, 4, 3, 5, 3, 3, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
		#  21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40
		#  sB sB Tp np  v fv tv nr  p sT sn sv sf st sr  E bp  M Kp  R
			6, 6, 9, 6, 6, 6, 6, 6, 6, 9, 6, 6, 6, 6, 6, 7, 7, 6, 3, 4,
		#  41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57
		#  Ds AE p1 p2 p4p10p30p60 fl Apf10 PC AL AU Mm La QI
			6, 5,10, 9, 9, 9, 9, 9, 3, 4, 6, 6, 6, 6, 5, 9, 7,
		],
		dtype=(
			"i4,i4,i4,i4,i4,i4,i4,i4,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,"
			"f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8,i4,i4,"
			"i4,i4,f8,f8,f8,f8,f8,f8,i4,i4,f8,f8,i4,i4,f8,f8,f8"
		),
		names=[
			"year", "doy", "hour", "bsrn", "id_imf", "id_sw", "n_imf", "n_plasma",
			"B_mag_avg", "B_mag", "theta_B", "phi_B",
			"B_x", "B_y_GSE", "B_z_GSE", "B_y_GSM", "B_z_GSM",
			"sigma_B_mag_avg", "sigma_B_mag",
			"sigma_B_x_GSE", "sigma_B_y_GSE", "sigma_B_z_GSE",
			"T_p", "n_p", "v_plasma", "phi_v", "theta_v", "n_alpha_n_p", "p_flow",
			"sigma_T", "sigma_n", "sigma_v",
			"sigma_phi_v", "sigma_theta_v", "sigma_na_np",
			"E", "beta_plasma", "mach", "Kp", "R", "Dst", "AE",
			"p_01MeV", "p_02MeV", "p_04MeV", "p_10MeV", "p_30MeV", "p_60MeV",
			"flag", "Ap", "f107_adj", "PC", "AL", "AU", "mach_mag", "Lya", "QI_p",
		]
	)
	sw = sw[sw["year"] != -1]
	ts = pd.to_datetime(
		[
			"{0:04d}.{1:03d} {2:02d}".format(yy, dd, hh)
			for yy, dd, hh in sw[["year", "doy", "hour"]]
		],
		format="%Y.%j %H",
	)
	sw_df = pd.DataFrame(sw, index=ts)
	# Adjust Kp to 0...9
	sw_df["Kp"] = 0.1 * sw_df["Kp"]
	return sw_df


def omnie_hourly(
	year,
	prefix=None,
	ext=None,
	local_path=None,
	url_base=None,
	cache=False,
):
	"""OMNI hourly data for year `year`

	Loads the OMNI hourly data for the given year,
	from the locally cached data.
	Use `local_path` to set a custom location if you
	have the omni data already available.

	Parameters
	----------
	year: int
		Year of the data.
	prefix: str, optional, default 'omni2'
		File prefix for constructing the file name as <prefix>_year.<ext>.
	ext: str, optional, default 'dat'
		File extension for constructing the file name as <prefix>_year.<ext>.
	local_path: str, optional
		Path to the locally stored data yearly files, defaults to the
		data location within the package.
	url_base: str, optional
		URL for the directory that contains the yearly files.
	cache: boolean, optional, default False
		Download files locally if they are not already available.

	Returns
	-------
	sw_df: pandas.DataFrame
		The parsed space weather data (hourly values).

		Raises an ``IOError`` if the file is not available.

	See Also
	--------
	read_omnie
	"""
	prefix = prefix or OMNI_PREFIX
	ext = ext or OMNI_EXT
	local_path = local_path or LOCAL_PATH
	url_base = url_base or OMNI_URL_BASE

	basename = "{0}_{1:04d}.{2}".format(prefix, year, ext)
	omnie_file = os.path.join(local_path, basename)

	# ensure that the file exists
	if not os.path.exists(omnie_file):
		warn("Could not find OMNI2 data {0}.".format(omnie_file))
		if cache:
			cache_omnie(
				year,
				prefix=prefix, ext=ext,
				local_path=local_path, url_base=url_base,
			)
		else:
			warn(
				"Local data files not found, pass `cache=True` "
				"or run `sw.cache_omnie()` to download the file."
			)

	return read_omnie(omnie_file)
