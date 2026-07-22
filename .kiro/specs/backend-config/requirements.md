# Requirements Document

## Introduction

`config.py` is the single, authoritative source of configuration constants for the Face Distance Estimation backend. Every module in the backend imports its runtime values from this file instead of hardcoding them locally. The file covers nine configuration sections — camera, face detection, distance estimation, angle estimation, calibration, confidence engine, visualization, logging, and application metadata — and exposes a `print_configuration()` helper for debugging. No CV logic, FastAPI code, or mutable global state is permitted in this module.

## Glossary

- **Config_Module**: The `config.py` file being specified.
- **Constant**: A module-level name written in `SCREAMING_SNAKE_CASE` whose value is never reassigned at runtime.
- **Consumer_Module**: Any other Python file in the backend that imports from `config.py`.
- **Section**: A logically grouped set of constants, separated by a comment block inside the file.
- **print_configuration()**: The single public helper function defined in `config.py` that prints all constants in a human-readable format.
- **EARS**: Easy Approach to Requirements Syntax — the pattern used to write all acceptance criteria below.

---

## Requirements

### Requirement 1: Module Structure and Purity

**User Story:** As a backend developer, I want `config.py` to contain only constants and one helper function, so that importing it never triggers side effects and every value is predictable.

#### Acceptance Criteria

1. THE Config_Module SHALL define all configuration values as module-level constants using `SCREAMING_SNAKE_CASE` names.
2. THE Config_Module SHALL NOT define any mutable global variables; specifically, it SHALL NOT define any module-level name whose value is a `list`, `dict`, `set`, or any object that exposes mutation methods (`append`, `update`, `__setitem__`, etc.) that could be called at runtime.
3. THE Config_Module SHALL NOT contain any of the following: OpenCV API calls (functions or classes from the `cv2` namespace), MediaPipe pipeline instantiation, FastAPI route declarations (`@app.get`, `@app.post`, etc.), or database connection/query statements (SQLAlchemy, psycopg2, sqlite3, etc.). The single permitted non-constant symbol is the `print_configuration` helper function.
4. THE Config_Module SHALL be importable with `import config` or `from config import <CONSTANT>` without executing any I/O, network access, subprocess calls, or computation beyond module-level constant assignment and function definition.
5. THE Config_Module SHALL declare type annotations for every constant using Python 3.11+ built-in types (e.g., `int`, `float`, `str`, `tuple[int, int, int]`).
6. THE Config_Module SHALL include a module-level docstring that states its purpose (single configuration source), lists all nine configuration sections by name, and provides at least one import usage example.

---

### Requirement 2: Camera Settings

**User Story:** As a camera module developer, I want all camera initialisation parameters centralised in `config.py`, so that I can change capture behaviour without touching camera code.

#### Acceptance Criteria

1. THE Config_Module SHALL define `CAMERA_INDEX: int` representing the OS index of the capture device, defaulting to `0`, with a valid range of `0` to `9` inclusive.
2. THE Config_Module SHALL define `FRAME_WIDTH: int` representing the requested capture width in pixels, defaulting to `640`, with a valid range of `1` to `7680` inclusive (1 px minimum to 8K width maximum).
3. THE Config_Module SHALL define `FRAME_HEIGHT: int` representing the requested capture height in pixels, defaulting to `480`, with a valid range of `1` to `4320` inclusive (1 px minimum to 8K height maximum).
4. THE Config_Module SHALL define `TARGET_FPS: int` representing the desired frames per second, defaulting to `30`, with a valid range of `1` to `240` inclusive.
5. THE Config_Module SHALL define `AUTO_EXPOSURE: int` representing the OpenCV `CAP_PROP_AUTO_EXPOSURE` flag value, defaulting to `1`, accepting only the values `0` (manual exposure) or `1` (auto-exposure enabled).
6. THE Config_Module SHALL be importable without side effects; importing it SHALL NOT open any camera device, allocate any hardware resource, or perform any file I/O.

---

### Requirement 3: Face Detection Settings

**User Story:** As a face-detector developer, I want detection thresholds and visualisation parameters in `config.py`, so that tuning them does not require touching detection logic.

#### Acceptance Criteria

1. THE Config_Module SHALL define `MIN_DETECTION_CONFIDENCE: float` in the range `[0.0, 1.0]` inclusive, defaulting to `0.7`.
2. THE Config_Module SHALL define `MAX_FACES: int` representing the maximum number of simultaneous faces to detect, defaulting to `1`, with a valid range of `1` to `10` inclusive.
3. THE Config_Module SHALL define `BOUNDING_BOX_COLOR: tuple[int, int, int]` as a BGR colour tuple, defaulting to `(0, 255, 0)`, where each integer component is in the range `[0, 255]` inclusive.
4. THE Config_Module SHALL define `BOUNDING_BOX_THICKNESS: int` in pixels, defaulting to `2`, with a valid range of `1` to `10` inclusive.
5. THE Config_Module SHALL define `TEXT_SIZE: float` as the OpenCV font scale, defaulting to `0.6`, with a valid range of greater than `0.0` up to and including `5.0`.

---

### Requirement 4: Distance Estimation Settings

**User Story:** As a distance-estimation developer, I want all physical constants and algorithm parameters centralised in `config.py`, so that measurement tuning is isolated from estimation logic.

#### Acceptance Criteria

1. THE Config_Module SHALL define `DEFAULT_FACE_WIDTH_CM: float` representing the average human face width in centimetres, defaulting to `14.3`, with a valid range of greater than `0.0` up to and including `50.0`.
2. THE Config_Module SHALL define `DEFAULT_FOCAL_LENGTH: float` as a placeholder focal length in pixels, defaulting to `615.0`, with a valid range of greater than `0.0`.
3. THE Config_Module SHALL define `MIN_MEASURABLE_DISTANCE_CM: float` representing the lower bound (in centimetres) below which a distance reading is considered unreliable and SHALL be discarded, defaulting to `20.0`, with a valid range of greater than `0.0`.
4. THE Config_Module SHALL define `MAX_MEASURABLE_DISTANCE_CM: float` representing the upper bound (in centimetres) above which a distance reading is considered unreliable and SHALL be discarded, defaulting to `500.0`, and SHALL be strictly greater than `MIN_MEASURABLE_DISTANCE_CM`.
5. THE Config_Module SHALL define `MOVING_AVERAGE_WINDOW: int` representing the number of consecutive distance readings averaged to smooth output, defaulting to `5`, with a valid range of `1` to `100` inclusive.

---

### Requirement 5: Angle Estimation Settings

**User Story:** As an angle-estimation developer, I want camera field-of-view parameters centralised in `config.py`, so that changing the camera lens does not require changes across multiple files.

#### Acceptance Criteria

1. THE Config_Module SHALL define `CAMERA_HORIZONTAL_FOV_DEG: float` representing the camera's horizontal field of view in degrees, defaulting to `60.0`, with a valid range of greater than `0.0` and less than `180.0` (exclusive on both bounds).
2. THE Config_Module SHALL define `CAMERA_VERTICAL_FOV_DEG: float` representing the camera's vertical field of view in degrees, defaulting to `45.0`, with a valid range of greater than `0.0` and less than `180.0` (exclusive on both bounds).
3. THE Config_Module SHALL define `MAX_ANGLE_DISPLAY_DEG: float` representing the maximum angle rendered on the UI radar, defaulting to `45.0`, with a valid range of greater than `0.0` up to and including the value of `CAMERA_HORIZONTAL_FOV_DEG`, and WHEN the calculated horizontal angle exceeds this value, THE Angle_Estimation_Module SHALL clamp the rendered angle to `MAX_ANGLE_DISPLAY_DEG`.
4. THE Angle_Estimation_Module SHALL import `CAMERA_HORIZONTAL_FOV_DEG`, `CAMERA_VERTICAL_FOV_DEG`, and `MAX_ANGLE_DISPLAY_DEG` exclusively from the Config_Module, and SHALL NOT contain hardcoded field-of-view values in any function or class.

---

### Requirement 6: Calibration Settings

**User Story:** As a calibration-module developer, I want calibration procedure parameters centralised in `config.py`, so that the calibration routine is driven entirely by configuration.

#### Acceptance Criteria

1. THE Config_Module SHALL define `CALIBRATION_DISTANCE_CM: float` representing the known physical distance in centimetres at which the calibration target is placed, defaulting to `100.0`, with a valid range of greater than `0.0` up to and including `500.0`.
2. THE Config_Module SHALL define `CALIBRATION_TOLERANCE: float` representing the maximum acceptable fractional deviation of an individual calibration sample from the session mean, defaulting to `0.1`, with a valid range of greater than `0.0` and less than `1.0` (exclusive on both bounds).
3. THE Config_Module SHALL define `CALIBRATION_SAMPLES: int` representing the number of frames captured and averaged during a calibration session, defaulting to `30`, with a valid range of `1` to `300` inclusive.

---

### Requirement 7: Confidence Engine Settings

**User Story:** As a confidence-engine developer, I want scoring weights and smoothing factors centralised in `config.py`, so that confidence tuning is possible without modifying engine logic.

#### Acceptance Criteria

1. THE Config_Module SHALL define `CONFIDENCE_LIGHTING_WEIGHT: float` representing the contribution of scene lighting to the confidence score, defaulting to `0.25`, with a valid range of `0.0` to `1.0` inclusive.
2. THE Config_Module SHALL define `CONFIDENCE_BLUR_WEIGHT: float` representing the contribution of image sharpness to the confidence score, defaulting to `0.25`, with a valid range of `0.0` to `1.0` inclusive.
3. THE Config_Module SHALL define `CONFIDENCE_DETECTION_STABILITY_WEIGHT: float` representing the contribution of detection-frame consistency to the confidence score, defaulting to `0.25`, with a valid range of `0.0` to `1.0` inclusive.
4. THE Config_Module SHALL define `CONFIDENCE_FACE_SIZE_WEIGHT: float` representing the contribution of face bounding-box area to the confidence score, defaulting to `0.25`, with a valid range of `0.0` to `1.0` inclusive.
5. THE Config_Module SHALL define `CONFIDENCE_SMOOTHING_FACTOR: float` in the range `[0.0, 1.0]` inclusive representing the exponential moving-average alpha, defaulting to `0.3`, where `0.0` produces no change (fully smoothed) and `1.0` passes raw values without smoothing.
6. THE sum of `CONFIDENCE_LIGHTING_WEIGHT`, `CONFIDENCE_BLUR_WEIGHT`, `CONFIDENCE_DETECTION_STABILITY_WEIGHT`, and `CONFIDENCE_FACE_SIZE_WEIGHT` SHALL equal `1.0` (allowing a floating-point tolerance of `1e-9`); IF the Confidence_Engine validates this constraint at startup, it SHALL raise a `ValueError` with a descriptive message identifying which weights were provided and their sum.
7. IF `CONFIDENCE_SMOOTHING_FACTOR` is set to a value outside `[0.0, 1.0]`, THE Confidence_Engine SHALL raise a `ValueError` with a message stating the invalid value and the required range.
8. IF `CONFIDENCE_LIGHTING_WEIGHT`, `CONFIDENCE_BLUR_WEIGHT`, `CONFIDENCE_DETECTION_STABILITY_WEIGHT`, or `CONFIDENCE_FACE_SIZE_WEIGHT` is set to a value outside `[0.0, 1.0]`, THE Confidence_Engine SHALL raise a `ValueError` with a message identifying the offending constant and its invalid value.

---

### Requirement 8: Visualization Settings

**User Story:** As a visualisation developer, I want all rendering parameters centralised in `config.py`, so that UI styling can be adjusted without altering rendering logic.

#### Acceptance Criteria

1. THE Config_Module SHALL define `RADAR_RADIUS: int` representing the radar overlay radius in pixels, defaulting to `150`, with a valid range of `1` to `240` inclusive.
2. THE Config_Module SHALL define `COLOR_RADAR: tuple[int, int, int]` as a BGR colour tuple for the radar overlay, defaulting to `(0, 200, 0)`, where each integer component is in the range `[0, 255]` inclusive.
3. THE Config_Module SHALL define `COLOR_DASHBOARD_BG: tuple[int, int, int]` as a BGR colour tuple for the dashboard background, defaulting to `(20, 20, 20)`, where each integer component is in the range `[0, 255]` inclusive.
4. THE Config_Module SHALL define `COLOR_TEXT: tuple[int, int, int]` as a BGR colour tuple for on-frame text, defaulting to `(255, 255, 255)`, where each integer component is in the range `[0, 255]` inclusive.
5. THE Config_Module SHALL define `COLOR_WARNING: tuple[int, int, int]` as a BGR colour tuple for warning indicators, defaulting to `(0, 0, 255)`, where each integer component is in the range `[0, 255]` inclusive.
6. THE Config_Module SHALL define `COLOR_SUCCESS: tuple[int, int, int]` as a BGR colour tuple for success indicators, defaulting to `(0, 255, 0)`, where each integer component is in the range `[0, 255]` inclusive.

---

### Requirement 9: Logging Settings

**User Story:** As an operations engineer, I want all logging parameters centralised in `config.py`, so that verbosity can be changed without searching through multiple files.

#### Acceptance Criteria

1. THE Config_Module SHALL define `LOG_LEVEL: str` as a standard Python logging level name, defaulting to `"INFO"`, accepting only the values `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, or `"CRITICAL"`.
2. THE Config_Module SHALL define `LOG_FORMAT: str` as a Python `logging` format string, defaulting to `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"`.
3. THE Config_Module SHALL define `DEBUG_MODE: bool` controlling whether verbose debug output is emitted, defaulting to `False`; WHEN `DEBUG_MODE` is `True`, THE effective log level SHALL be `"DEBUG"` regardless of the value of `LOG_LEVEL`.
4. IF `LOG_LEVEL` is set to a value not in the permitted set (`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`), THE logging initialisation code SHALL raise a `ValueError` with a message identifying the invalid value and listing the permitted values.

---

### Requirement 10: Application Metadata

**User Story:** As a developer, I want application identity constants in `config.py`, so that version information and authorship are traceable from a single location.

#### Acceptance Criteria

1. THE Config_Module SHALL define `APP_NAME: str` with the application display name, defaulting to `"Face Distance Estimation"`, with a maximum length of `100` characters.
2. THE Config_Module SHALL define `APP_VERSION: str` following the format `MAJOR.MINOR.PATCH` where `MAJOR`, `MINOR`, and `PATCH` are each non-negative integers with no leading zeros, defaulting to `"1.0.0"`.
3. THE Config_Module SHALL define `APP_AUTHOR: str` as a placeholder for the project author, defaulting to `"Author"`, with a maximum length of `100` characters.
4. THE constants `APP_NAME`, `APP_VERSION`, and `APP_AUTHOR` SHALL be importable directly from the Config_Module using `from config import APP_NAME, APP_VERSION, APP_AUTHOR`.

---

### Requirement 11: Configuration Debug Helper

**User Story:** As a developer, I want a `print_configuration()` function that prints every constant grouped by section, so that I can quickly verify the active configuration during development.

#### Acceptance Criteria

1. THE Config_Module SHALL define exactly one public function: `print_configuration() -> None`.
2. WHEN `print_configuration()` is called, THE function SHALL print all nine configuration sections in the same order they are declared in the module, with each constant rendered as `  NAME = value` (two leading spaces, constant name left-aligned, equals sign, then the value).
3. WHEN `print_configuration()` is called, each section SHALL be preceded by a banner line of the form `── <Section Title> ───…─` (using U+2500 box-drawing characters) and followed by a blank line to visually separate it from the next section.
4. THE `print_configuration` function SHALL include a docstring describing its purpose, the output format, and an example of the printed output.
5. WHEN `print_configuration()` is called, THE function SHALL print to standard output using the built-in `print` function, requiring no logging framework to be configured.
6. WHEN `print_configuration()` is called, THE function SHALL print a single preamble header line before the first section containing `APP_NAME` and `APP_VERSION` (e.g., `"Face Distance Estimation  v1.0.0  — Active Configuration"`).
