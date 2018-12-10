# Changelog
All notable changes to this project will be documented in this file.

The format is based on [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/).

## [2.0.0] - 2019-yy-xx
### Added
- GUI (yay!) coded in Python using [PySimpleGUI](https://pypi.org/project/PySimpleGUI/).
- Documentation for the preparation of input data (displayed in GUI).
- Program part SD2OPP (coded in Python) for the calculation of OPPs from MEM-reconstructed scatterer densities.
- Files to comply with the LGPL v3 license of PySimpleGUI.
- Logo and icons.
- PDF2OPP_2D: Possibility to read temperature from JANA2006’s `*.m90` file.
- PDF2OPP_3D: Possibility to specify temperature and output file name *via* command line.

### Changed
- PDF2OPP_2D and PDF2OPP_3D: Ported to Fortran2008. 
- Common release of former CalcOPP (for 2D data) and CalcOPP-3D (for 3D data) under the name CalcOPP.
- Renaming of former CalcOPP to PDF2OPP_2D and CalcOPP-3D to PDF2OPP_3D.
- Development at [GitHub](https://github.com/dewiedem/calcopp).
- Merged documentation files.
- Unification of documentation strings.

### Removed
- PDF2OPP_2D and PDF2OPP_3D: Interactive input facilities (obsolete because of GUI).
- PDF2OPP_2D: Alternative command-line parameters.
- Extensive information on usage in README (obsolete because of explanations in GUI and command-line parameter `-h` for executables).

## [1.6.1]
### Fixed
- Rebuilt broken CalcOPP windows binaries against gcc-4.9.3.

## [1.6.0]
### Added
- Extended documentation (`Readme.txt`) to include purpose and architecture information.

### Changed
- Put under the MIT License to make it available in public repositories. Altered all files accordingly.
- Included DOI in new citation.

### Fixed
- Corrected a typo in `--help` output.

## [1.5.0]
### Added
- Processing of error maps.
- Menu to select job in interactive mode.
- Added help text.
- Added citation to standard output.
- Versions for Windows and Linux (32bit, 64bit).
- Added documentation for new features.

### Changed
- More verbose output to monitor status.
- Parsing of whole command line for current and future use.

## [1.0.0]
### Added
- First production version with basic functionality.
