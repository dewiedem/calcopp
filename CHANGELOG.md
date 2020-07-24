# Changelog
All notable changes to CalcOPP will be documented in this file; its format is based on [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/). This project adheres to [*Semantic Versioning*](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- `build.cmd` and `build.sh`: Check for existence before changing directories.

## [2.0.3] - 2020-07-24
### Changed
- Description part in README to be more precise with respect to the calculation.
- Bounced all version strings.
- `calcopp-gui`: Some entity names to match new ones in PySimpleGUI.
- `calcopp-gui`: Text refreshing in manual window to comply with new PySimpleGUI mechanism.

### Fixed
- `pdf2opp_2d` and `pdf2opp_3d`: Displayed version numbers.
- `calcopp-gui`: Error when using file paths containing blanks with `pdf2opp_2d` and `pdf2opp_3d`.
- `build.cmd`: No longer using Python's `-O` flag when freezing with PyInstaller because of packaging errors.
- `build.cmd`: Re-enabled UPX for debugged version 3.96.
- `build.cmd` and `build.sh`: Hidden imports for PyInstaller no longer needed.
- `build.sh`: Not using PyInstaller's `--strip` flag because of incompatbility with NumPy 1.19.1.

## [2.0.2] - 2020-01-13
### Changed
- `calcopp-gui`: New dark color scheme.
- Bumped all version and date strings.
- Added quirk to enable freezing with PyInstaller 3.6.
- `pdf2opp_2d` and `pdf2opp_3d`: Changed source-code file extensions to `*.f90`, the standard for free-form Fortran.

### Fixed
- `calcopp-gui`: Broken color theme (new version of PySimpleGUI).
- `calcopp-gui`: Broken displaying in the field “Information and Manual” (new version of PySimpleGUI).
- `pdf2opp_2d` and `pdf2opp_3d`: Correctly assigned dialect as Fortran 2018 (non-constant error stop codes).

### Removed
- `calcopp-gui`: Workaround opening underlying command window in Windows version.
- `calcopp-gui`: UPX compression for Windows version (causing error in Windows 10).
- 32 bit builds.

## [2.0.1] - 2019-07-16
### Changed
- Defined Boltzmann constant as ratio of two exact values (CODATA 2018).

### Fixed
- `pdf2opp_3d`: Ability to handle zeros as PDF input values.

## [2.0.0] - 2019-04-12
### Added
- Binaries for Windows (64/32 bit) and Linux (64 bit).
- Test input data.
- Build scripts for Windows and Linux.
- `calcopp-gui`: Menu items to access `README` and `CHANGELOG`.
- `calcopp-gui`: Quirks to freeze to Windows binary with desired behavior.

### Changed
- Bumped all version and status strings.
- Moved external files into separate data directory.
- Made `README` more concise.
- `calcopp-gui`: The field “Information and Manual” is now read-only.
- `calcopp-gui`: Deleted explicit `do_not_clear` and `grab_anywhere` flags (defaults with new PySimpleGUI version).
- `calcopp-gui`: Improved error messages for invalid/inconsistent input.
- `calcopp-gui`: File extension for output files no longer automatically added (before, file name was garbled when editing the extension).

### Fixed
- Displayed DOI.
- Documentation of software versions and installation requirements.
- Several typos throughout.
- `calcopp-gui`: Code for external file execution to run under Windows *and* Linux.

## [2.0.0-rc.1] - 2019-01-02
### Added
- GUI (yay!) coded in Python using [PySimpleGUI](https://pypi.org/project/PySimpleGUI/).
- Documentation for the preparation of input data (displayed in GUI).
- Program part `sd2opp` (coded in Python) for the calculation of OPPs from MEM-reconstructed scatterer densities.
- Files to comply with LGPL v3 license of PySimpleGUI.
- Files to comply with license of NumPy.
- Logo and icons.
- `pdf2opp_2d`: Possibility to read temperature from JANA2006’s `*.m90` file.
- `pdf2opp_3d`: Possibility to specify temperature and output file name *via* command line.

### Changed
- Common release of former CalcOPP (for 2D data) and CalcOPP-3D (for 3D data) under the name CalcOPP.
- Renaming of former CalcOPP to `pdf2opp_2d` and former CalcOPP-3D to `pdf2opp_3d`.
- Development at [GitHub](https://github.com/dewiedem/calcopp).
- Merged documentation files.
- Unification of documentation strings.
- `pdf2opp_2d` and `pdf2opp_3d`: Rewritten array handling for faster calculation.
- `pdf2opp_2d` and `pdf2opp_3d`: Rewritten routines for more simplicity.
- `pdf2opp_2d` and `pdf2opp_3d`: Improved input checks.
- `pdf2opp_2d` and `pdf2opp_3d`: Improved text output.
- `pdf2opp_2d` and `pdf2opp_3d`: Ported to Fortran2008.
- `pdf2opp_2d` and `pdf2opp_3d`: Improved code readability.
- `pdf2opp_2d`: **Now calculates OPPs in eV instead of meV.**
- `pdf2opp_2d`: **New algorithm for error estimation (see `README`).** Before, values were fully valid only for relative PDF errors δ*p* < 1.5%, rough estimates for δ*p* < 15%, and wrong for δ*p* > 15%.
- `pdf2opp_2d`: Stripped unnecessary blanks bloating output files.
- `pdf2opp_3d`: Improved VESTA output file for direct display.

### Removed
- `pdf2opp_2d` and `pdf2opp_3d`: Interactive input facilities (obsolete because of GUI).
- `pdf2opp_2d`: Alternative command-line parameters.
- Extensive information on usage in `README` (obsolete because of explanations in GUI and command-line parameter `-h` for executables).

## [1.6.1] - 2015-09-03
### Fixed
- Rebuilt broken Windows binaries against GFortran 4.9.3.

## [1.6] - 2015-09-03
### Added
- Extended documentation (`Readme.txt`) to include purpose and architecture information.

### Changed
- Put under the MIT License to make it available in public repositories. Altered all files accordingly.
- Included DOI in new citation.

### Fixed
- Typo in `--help` output.

## 1.5 - 2015-06-24
### Added
- Processing of error maps.
- Menu to select job in interactive mode.
- Help text.
- Citation in standard output.
- Versions for Windows and Linux (32/64 bit).
- Documentation for new features.

### Changed
- More verbose output to monitor status.
- Parsing of whole command line for current and future use.

## 1.0 - 2013-07-08
### Added
- First production version with basic functionality.

[2.0.3]: https://github.com/dewiedem/calcopp/releases/tag/v2.0.3
[2.0.2]: https://github.com/dewiedem/calcopp/releases/tag/v2.0.2
[2.0.1]: https://github.com/dewiedem/calcopp/releases/tag/v2.0.1
[2.0.0]: https://github.com/dewiedem/calcopp/releases/tag/v2.0.0
[2.0.0-rc.1]: https://github.com/dewiedem/calcopp/releases/tag/v2.0.0-rc.1
[1.6.1]: https://doi.org/10.6084/m9.figshare.1461721.v4
[1.6]: https://doi.org/10.6084/m9.figshare.1461721.v2
