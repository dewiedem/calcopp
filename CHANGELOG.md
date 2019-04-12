# Changelog
All notable changes to CalcOPP will be documented in this file; its format is based on [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/). This project adheres to [*Semantic Versioning*](https://semver.org/spec/v2.0.0.html).

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

## [2.0.0-rc1] - 2019-01-02
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
- Rebuilt broken CalcOPP windows binaries against gcc-4.9.3.

## [1.6.0] - 2015-09-03
### Added
- Extended documentation (`Readme.txt`) to include purpose and architecture information.

### Changed
- Put under the MIT License to make it available in public repositories. Altered all files accordingly.
- Included DOI in new citation.

### Fixed
- Typo in `--help` output.

## 1.5.0 - 2015-06-24
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

## 1.0.0 - 2013-07-08
### Added
- First production version with basic functionality.

[2.0.0]: https://github.com/dewiedem/calcopp/releases/tag/v.2.0.0
[2.0.0-rc1]: https://github.com/dewiedem/calcopp/releases/tag/v.2.0.0-rc1
[1.6.1]: https://doi.org/10.6084/m9.figshare.1461721.v4
[1.6.0]: https://doi.org/10.6084/m9.figshare.1461721.v2
