Changelog
=========

v0.4.0 (unreleased)
-------------------

### New

- Supports space weather Hp30 and Hp60 index data from GFZ Potsdam
  https://kp.gfz-potsdam.de/en/hp30-hp60, https://doi.org/10.5880/HPO.0003
- Raises a `UserWarning` when downloading the data fails

### Fixes

- Compatibility with newer `setuptools` versions that will remove support
  for `pkg_resources`
- Avoids inadvertently updating the local data files when running the test
  suite locally
- Formatting fixes for the documentation

### Changes

- Updates space weather indices from celestrak (observed until 2025-07-16),
  differences throughout the whole period, ISN and F10.7 data changed.
- Reduces server access when testing data updating
- CI updates


v0.3.0 (2024-04-04)
-------------------

### New

- Supports space weather index data from GFZ Potsdam
  https://kp.gfz-potsdam.de/en/

### Fixes

- Fixes downloading OMNI2 on Windows (https://github.com/st-bender/pyspaceweather/issues/2)

### Changes

- Updates space weather indices from celestrak (observed until 2024-04-01)


v0.2.4 (2024-02-14)
-------------------

### Changes

- Updates space weather indices from celestrak (observed until 2024-02-13)
- CI updates


v0.2.3 (2023-11-01)
-------------------

### Changes

- Updates space weather indices from celestrak (observed until 2023-10-31)
- Fixes documentation rendering on readthedocs
  (https://pyspaceweather.readthedocs.io/)
- CI updates


v0.2.2 (2022-11-24)
-------------------

### Fixes

- Fixes an unclosed resource file warning when calculating the file age
  (GH https://github.com/st-bender/pyspaceweather/issues/1)

### Updates

- Uses pytest.fixtures to speed up tests


v0.2.1 (2022-02-18)
-------------------

### New

- Support for OMNI2 missing values


v0.2.0 (2022-02-13)
-------------------

### New

- Support for OMNI2 (extended) 1-hourly text files from <https://omniweb.gsfc.nasa.gov/ow.html>
  with tests and documentation

### Changes

- Restructuring and renaming of the internal (sub)modules
- Other documentation updates


v0.1.1 (2022-01-25)
-------------------

### Changes

- Updated data files
- Fixed, updated, and improved tests to increase code coverage
- Uses Github actions for CI and CD


v0.1.0 (2021-09-20)
-------------------

First official beta release.
