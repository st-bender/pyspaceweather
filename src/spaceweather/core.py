# Copyright (c) 2020--2022 Stefan Bender
#
# This module is part of pyspaceweather.
# pyspaceweather is free software: you can redistribute it or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, version 2.
# See accompanying COPYING.GPLv2 file or http://www.gnu.org/licenses/gpl-2.0.html.
"""Python interface for space weather indices

General file handling functions for space weather data
"""
import errno
import os

import requests


def _assert_file_exists(f):
	if not os.path.exists(f):
		raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), f)


def _dl_file(swpath, url):
	with requests.get(url, stream=True) as r:
		if r.status_code != requests.codes.ok:
			return
		with open(swpath, 'wb') as fd:
			for chunk in r.iter_content(chunk_size=1024):
				fd.write(chunk)
