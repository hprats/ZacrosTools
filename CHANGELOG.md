## [1.01] - 13-Oct-2024

### Added
- Added data validation and error handling in `plot_result.py`.
- *ZacrosTools* is now compatible with multidentate species.
- *ZacrosTools* is now compatible with default lattices.

### Changed
- The `detect_issues` function now only considers the specified window percent.
- Default `window_percent` for `detect_issues` changed from `[50, 100]` to `[30, 100]`.

### Fixed
- Bug fix for cases where vibrational energies of 0.0 are specified in the reaction model. 

### Improved
- Improved the documentation in ReadTheDocs. 

## [1.0] - 06-Sep-2024

Initial release.
