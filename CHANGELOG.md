# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-05-26

### Added

- Player management system
  - Add player
  - Edit player
  - Delete player
  - Search player

- Tournament management
  - Create tournament
  - Activate tournament
  - Register participants

- Swiss pairing engine
  - Automatic pairing generation
  - Bye support
  - Pairing history tracking

- Result management
  - White win
  - Black win
  - Draw result

- Standings system
  - Point calculation
  - Buchholz tie-break calculation
  - Automatic ranking updates

- SQLite database integration

- Tkinter desktop interface

### Fixed

- Fixed multiple f-string syntax issues
- Fixed tournament round field references
- Fixed Tkinter event binding issues
- Fixed database query errors
- Fixed pairing generation stability issues

### Known Issues

- Color balancing is not implemented.
- Advanced Swiss pairing restrictions are not fully supported.
- Tournament export functionality is not available.