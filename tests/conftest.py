import pytest


def pytest_addoption(parser):
	parser.addoption(
		"--run-online",
		action="store_true",
		default=False,
		help="Run online tests",
	)


def pytest_collection_modifyitems(config, items):
	if not config.getoption("--run-online"):
		skipper = pytest.mark.skip(reason="Only run when --run-online is given")
		for item in items:
			if "online" in item.keywords:
				item.add_marker(skipper)
