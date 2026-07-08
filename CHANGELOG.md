# Changelog

All notable changes to this project will be documented in this file.

## [1.2.1] - 2026-07-08

### Fixed
* **CustomTkinter Compatibility Fix**: Fixed a critical crash where generating pairings or updating enrolled players failed due to using the deprecated Tkinter `.config()` method instead of CustomTkinter's `.configure()` on label widgets (`round_label` and `enrolled_count_label`).
* **Format Case-Sensitivity Fix**: Improved tournament format validation to properly handle case-insensitive checks (`'elimination'` vs `'ELIMINATION'`) and added fallback values when retrieving tournament types from the database.
* Fixed an issue where the pairing treeview appeared empty or unresponsive after clicking "Generate Pairings" in Elimination mode.

## [1.2.0] - 2026-07-07

### Added
* Single Elimination tournament format support alongside the Swiss system.
* Modern Dark Mode interface powered by CustomTkinter.
* Auto-finish trigger: Tournament automatically finishes and updates status when the last round is complete.
* Epic Winner Announcement pop-up upon tournament completion.
* Custom CiptaCode logo icon for the main window, taskbar, and pop-up dialogs.
* Separated `elimination.py` engine for better code structure and scalability.

### Changed
* Completely revamped the GUI from standard Tkinter to CustomTkinter for a more professional look.
* Updated database schema to include a `format` column in the `tournaments` table.
* Improved tournament creation by replacing the manual round input with a safer dropdown option menu.
* Dynamic recommended rounds calculator based on the selected tournament format.

### Fixed
* Fixed a major logical bug where the tournament status would get stuck on 'ongoing' even after all matches were completed.
* Fixed the UI bug where treeview text was hard to read (now perfectly configured for dark mode).

---

## [1.1.0] - 2026-06-21

### Fixed
* Fixed data input failure bugs.
* Fixed broken UI layouts.

---

## [1.0.0] - 2026-05-26

### Added
* Player management system
  * Add player
  * Edit player
  * Delete player
  * Search player
* Tournament management
  * Create tournament
  * Activate tournament
  * Register participants
* Swiss pairing engine
  * Automatic pairing generation
  * Bye support
  * Pairing history tracking
* Result management
  * White win
  * Black win
  * Draw result
* Standings system
  * Point calculation
  * Buchholz tie-break calculation
  * Automatic ranking updates
* SQLite database integration
* Tkinter desktop interface

### Fixed
* Fixed multiple f-string syntax issues.
* Fixed tournament round field references.
* Fixed Tkinter event binding issues.
* Fixed database query errors.
* Fixed pairing generation stability issues.

### Known Issues
* Color balancing is not implemented.
* Advanced Swiss pairing restrictions are not fully supported.
* Tournament export functionality is not available.
