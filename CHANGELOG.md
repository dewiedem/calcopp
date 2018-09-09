# Changelog
All notable changes to this project will be documented in this file.

The format is based on [*Keep a Changelog*](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
### Added
- Added GUI based on [gtk-fortran](https://github.com/jerryd/gtk-fortran).
- Routines to calculate OPP from MEM-reconstructed scatterer density.

### Changed
- Switched to GPL v3 to include gtk-fortran.

### Removed
- Hard-coded descriptions, menus, and help texts from program parts.

## [2.0.0] - 2018-yy-xx
### Added
- New program part CalcOPP-3D.

### Changed
- First common release of CalcOPP (for 2D data) and CalcOPP-3D under the name CalcOPP. The included versions are identical with CalcOPP 1.6.1 and CalcOPP-3D 1.0.0. 
- Convergent development at [GitHub](https://github.com/dewiedem/calcopp).
- Merged documentation files.

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