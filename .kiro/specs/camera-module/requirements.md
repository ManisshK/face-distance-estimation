# Requirements Document

## Introduction

`camera.py` encapsulates all webcam lifecycle management for the Face Distance Estimation backend. It provides a single `Camera` class whose sole responsibility is opening, reading from, and releasing an OpenCV `VideoCapture` device. The module contains no face-detection logic, no distance or angle estimation, no calibration, no confidence scoring, and no FastAPI route definitions. All hardware parameters are imported from `config.py`; no values are hardcoded locally.

## Glossary

- **Camera**: The Python class defined in `camera.py` that manages a single webcam device.
- **VideoCapture**: The `cv2.VideoCapture` object used internally by `Camera` to interface with the OS capture device.
- **Frame**: A single `numpy.ndarray` image returned by `cv2.VideoCapture.read()`.
- **Config_Module**: The `config.py` file that is the sole source of configuration constants.
- **CAMERA_INDEX**: The OS device index passed to `cv2.VideoCapture()`; imported from Config_Module.
- **FRAME_WIDTH / FRAME_HEIGHT**: Requested capture dimensions in pixels; imported from Config_Module.
- **TARGET_FPS**: Desired frames per second; imported from Config_Module.
- **AUTO_EXPOSURE**: `cv2.CAP_PROP_AUTO_EXPOSURE` flag value; imported from Config_Module.
- **LOG_LEVEL / LOG_FORMAT**: Logging configuration; imported from Config_Module.
- **EARS**: Easy Approach to Requirements Syntax — the pattern used for all acceptance criteria.

---

## Requirements

### Requirement 1: Module Scope and Single Responsibility

**User Story:** As a backend developer, I want `camera.py` to contain only webcam-management code, so that the module has a single, well-defined responsibility and does not mix concerns.

#### Acceptance Criteria

1. THE Camera module SHALL define exactly one public class: `Camera` (where "public" means a name not prefixed with `_`); private helper classes are permitted.
2. THE Camera module SHALL NOT import from `cv2.face`, `mediapipe`, `fastapi`, `sqlalchemy`, `psycopg2`, or `sqlite3`; the only permitted `cv2` usage is `VideoCapture`, `CAP_PROP_*` constants, `imshow`, `waitKey`, and `destroyAllWindows`.
3. THE Camera module SHALL NOT contain hardcoded literals for the five camera configuration symbols `CAMERA_INDEX`, `FRAME_WIDTH`, `FRAME_HEIGHT`, `TARGET_FPS`, or `AUTO_EXPOSURE`; all five SHALL be imported from the Config_Module.
4. THE Camera module SHALL NOT call `print()` anywhere except inside the `if __name__ == "__main__"` block; all other diagnostic output SHALL use the standard Python `logging` module.
5. THE Camera module SHALL be compatible with Python 3.11 and above; every public method SHALL carry complete type annotations for both parameter types and return type, conforming to PEP 484.

---

### Requirement 2: Camera Initialisation

**User Story:** As a backend developer, I want `Camera.__init__()` to prepare internal state only, so that constructing a `Camera` object never opens a hardware device.

#### Acceptance Criteria

1. WHEN `Camera()` is instantiated, THE Camera SHALL initialise internal variables only and SHALL NOT call any `cv2.VideoCapture` constructor or perform any operating-system-level device access.
2. THE `__init__` method SHALL accept no arguments beyond `self`.
3. WHEN `Camera()` is instantiated, THE Camera SHALL set its internal `VideoCapture` reference to `None` with the type annotation `Optional[cv2.VideoCapture]`.
4. WHEN the Camera module is imported, THE module SHALL call `logging.basicConfig()` with `level` set to the value of `LOG_LEVEL` from the Config_Module and `format` set to `LOG_FORMAT` from the Config_Module.
5. THE `__init__` method SHALL include a docstring that states it prepares internal state only and explicitly states that no camera device is opened.

---

### Requirement 3: Camera Start

**User Story:** As a backend developer, I want `Camera.start()` to open and configure the webcam, so that hardware access is explicit and auditable.

#### Acceptance Criteria

1. WHEN `start()` is called, THE Camera SHALL create a `cv2.VideoCapture` object using `CAMERA_INDEX` imported from the Config_Module.
2. WHEN `start()` is called, THE Camera SHALL set `cv2.CAP_PROP_FRAME_WIDTH` to `FRAME_WIDTH`, `cv2.CAP_PROP_FRAME_HEIGHT` to `FRAME_HEIGHT`, `cv2.CAP_PROP_FPS` to `TARGET_FPS`, and `cv2.CAP_PROP_AUTO_EXPOSURE` to `AUTO_EXPOSURE`, all imported from the Config_Module.
3. WHEN `start()` is called and the camera opens successfully, THE Camera SHALL log a message at INFO level indicating the camera index and that the camera opened successfully.
4. IF `start()` is called and `cv2.VideoCapture.isOpened()` returns `False`, THEN THE Camera SHALL call `cv2.VideoCapture.release()` on the failed capture object and raise a `RuntimeError` whose message includes the value of `CAMERA_INDEX`.
5. WHEN `start()` is called and the camera opens successfully, THE Camera SHALL log the actual resolution and FPS as reported by OpenCV at INFO level.
6. THE `start()` method SHALL have return type `None`.
7. WHEN `start()` is called on a `Camera` instance that is already open (i.e. `is_open()` returns `True`), THE Camera SHALL return immediately without creating a new `VideoCapture` object or altering any state.

---

### Requirement 4: Frame Reading

**User Story:** As a backend developer, I want `Camera.read()` to return a `(success, frame)` tuple matching the OpenCV convention, so that callers can consume frames without knowing internal state.

#### Acceptance Criteria

1. WHEN `read()` is called and `start()` has previously succeeded, THE Camera SHALL call `cv2.VideoCapture.read()` and return `(True, frame)` where `frame` is the `numpy.ndarray` returned by OpenCV.
2. WHEN `read()` is called and `cv2.VideoCapture.read()` returns a failure flag (first element `False`) without raising an exception, THE Camera SHALL log a WARNING message that includes `CAMERA_INDEX` and return `(False, None)` without raising an exception.
3. IF `read()` is called and `self._capture is None` (i.e. `start()` has never been called), THEN THE Camera SHALL raise a `RuntimeError` with a message that includes the text "start()" to indicate the required prerequisite call.
4. THE `read()` method SHALL have return type `tuple[bool, np.ndarray | None]`, and its docstring SHALL describe the two return cases `(True, frame)` and `(False, None)`, and SHALL document the `RuntimeError` raised when the camera is not started.
5. WHEN `read()` calls `cv2.VideoCapture.read()` and that call raises an exception, THE Camera SHALL log the exception at ERROR level with `exc_info=True` and return `(False, None)` without re-raising the exception.

---

### Requirement 5: Camera Open Status

**User Story:** As a backend developer, I want `Camera.is_open()` to report whether the webcam is currently active, so that callers can guard against invalid states without inspecting internals.

#### Acceptance Criteria

1. WHEN `is_open()` is called before `start()`, THE Camera SHALL return `False`.
2. WHEN `is_open()` is called after a successful `start()` and before `stop()`, THE Camera SHALL return `True` only if the underlying `VideoCapture.isOpened()` also returns `True`.
3. WHEN `is_open()` is called after `stop()`, THE Camera SHALL return `False`.
4. THE `is_open()` method SHALL have return type `bool`, accept no arguments beyond `self`, and its docstring SHALL state that the return value reflects live hardware state via `VideoCapture.isOpened()` rather than a cached flag.
5. WHEN `is_open()` is called after `start()` raises a `RuntimeError` (i.e. the camera failed to open), THE Camera SHALL return `False`.

---

### Requirement 6: Camera Stop

**User Story:** As a backend developer, I want `Camera.stop()` to safely release the webcam regardless of state, so that resources are never leaked and repeated calls do not raise errors.

#### Acceptance Criteria

1. WHEN `stop()` is called on an open camera, THE Camera SHALL call `cv2.VideoCapture.release()` and log a message at INFO level that includes `CAMERA_INDEX` and states the device has been released.
2. WHEN `stop()` is called on a camera that is already stopped, was never started, or has `self._capture is None`, THE Camera SHALL return silently without raising any exception; this behaviour SHALL hold for any number of repeated calls.
3. WHEN `stop()` is called, THE Camera SHALL set its internal `_capture` attribute to `None` so that a subsequent call to `is_open()` returns `False`.
4. THE `stop()` method SHALL have return type `None`, and its docstring SHALL describe the idempotent behaviour and its effect on `is_open()`.

---

### Requirement 7: Actual Resolution Query

**User Story:** As a backend developer, I want `Camera.get_resolution()` to return the actual capture dimensions reported by OpenCV, so that callers know what the hardware is delivering rather than what was requested.

#### Acceptance Criteria

1. WHEN `get_resolution()` is called and `is_open()` returns `True`, THE Camera SHALL query `cv2.CAP_PROP_FRAME_WIDTH` and `cv2.CAP_PROP_FRAME_HEIGHT` from the live `VideoCapture` and return `(width, height)` as `(int, int)` with width as the first element.
2. THE `get_resolution()` method SHALL NOT return the values of `FRAME_WIDTH` or `FRAME_HEIGHT` from the Config_Module; it SHALL always call `VideoCapture.get()` to obtain current property values.
3. IF `get_resolution()` is called and `is_open()` returns `False`, THEN THE Camera SHALL raise a `RuntimeError` whose message identifies `get_resolution()` as the caller and instructs the user to call `start()` first.
4. THE `get_resolution()` method SHALL have return type `tuple[int, int]`, and its docstring SHALL describe the return value, state that it reflects live OpenCV properties (not config values), and document the `RuntimeError`.
5. WHEN `get_resolution()` is called and `VideoCapture.get()` returns `0.0` for either property (indicating the driver does not report the value), THE Camera SHALL return `(0, 0)` without raising an exception, allowing the caller to detect the unsupported condition.

---

### Requirement 8: Actual FPS Query

**User Story:** As a backend developer, I want `Camera.get_fps()` to return the FPS actually reported by OpenCV, so that callers detect hardware limitations rather than assuming the configured target was applied.

#### Acceptance Criteria

1. WHEN `get_fps()` is called and `is_open()` returns `True`, THE Camera SHALL query `cv2.CAP_PROP_FPS` from the live `VideoCapture` and return it as `float`, including `0.0` when the driver does not report a rate.
2. THE `get_fps()` method SHALL NOT return the value of `TARGET_FPS` from the Config_Module; it SHALL always call `VideoCapture.get(cv2.CAP_PROP_FPS)` to obtain the current value.
3. IF `get_fps()` is called and `is_open()` returns `False`, THEN THE Camera SHALL raise a `RuntimeError` whose message identifies `get_fps()` as the caller and instructs the user to call `start()` first.
4. THE `get_fps()` method SHALL have return type `float`, and its docstring SHALL describe the return value, note that `0.0` is a valid return when the driver does not report FPS, and document the `RuntimeError`.

---

### Requirement 9: Logging

**User Story:** As an operations engineer, I want all Camera events logged with the standard Python logging module, so that diagnostic messages are consistent with the rest of the backend.

#### Acceptance Criteria

1. THE Camera class SHALL use `logging.getLogger(__name__)` to obtain its logger instance; it SHALL NOT create a named logger with a hardcoded string.
2. THE Camera module SHALL call `logging.basicConfig()` at module level using `level` derived from `LOG_LEVEL` and `format` set to `LOG_FORMAT`, both imported from the Config_Module; IF `LOG_LEVEL` is not a recognised Python logging level name, THE module SHALL fall back to `logging.INFO`.
3. WHEN `start()` is called, THE Camera SHALL emit an INFO log before attempting to open the device and a second INFO log after the device opens successfully, with the second message including the device index.
4. WHEN `stop()` releases an open device, THE Camera SHALL emit an INFO log that includes the device index.
5. WHEN `cv2.VideoCapture.read()` returns a failure flag, THE Camera SHALL emit a WARNING log that includes the device index.
6. WHEN `cv2.VideoCapture.read()` raises an exception, THE Camera SHALL emit an ERROR log with `exc_info=True`.
7. THE Camera module SHALL NOT call `print()` outside of the `if __name__ == "__main__"` guard block.

---

### Requirement 10: `__main__` Test Block

**User Story:** As a developer, I want a runnable `__main__` block in `camera.py`, so that I can manually verify webcam operation from the command line without writing a separate test script.

#### Acceptance Criteria

1. WHEN `camera.py` is executed directly, THE `__main__` block SHALL instantiate `Camera`, call `start()`, enter a display loop that calls `cam.read()`, shows successfully captured frames via `cv2.imshow()`, and exits the loop when the user presses the lowercase `q` key (detected via `cv2.waitKey(1) & 0xFF == ord("q")`).
2. WHEN `cam.read()` returns `(False, None)` inside the display loop, THE `__main__` block SHALL skip the `cv2.imshow()` call and continue to the next iteration without exiting.
3. WHEN the display loop exits for any reason, THE `__main__` block SHALL call `cam.stop()` and `cv2.destroyAllWindows()` inside a `finally` block to guarantee resource release.
4. WHEN `start()` raises a `RuntimeError`, THE `__main__` block SHALL write the error message to `sys.stderr` and call `sys.exit(1)`.
5. THE `__main__` block SHALL contain only the following operations: instantiate `Camera`, call `start()`, loop-read-display, exit on `q`, call `stop()` and `cv2.destroyAllWindows()` in `finally`; it SHALL NOT contain face detection, distance logic, or any other domain concerns.
