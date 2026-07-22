"""
config.py — Single configuration source for the Face Distance Estimation backend.

Every backend module MUST import its runtime values from this file instead of
hardcoding them locally.  This module is intentionally free of side effects:
importing it performs no I/O, no computation, and no external calls beyond
simple constant assignment.

Configuration sections
----------------------
1.  Camera Settings
2.  Face Detection Settings
3.  Distance Estimation Settings
4.  Angle Estimation Settings
5.  Calibration Settings
6.  Confidence Engine Settings
7.  Visualization Settings
8.  Logging Settings
9.  Application Metadata

Usage
-----
    from app.config import FRAME_WIDTH, FRAME_HEIGHT
    import app.config as config; config.print_configuration()
"""

# ---------------------------------------------------------------------------
# 1. Camera Settings
# ---------------------------------------------------------------------------

CAMERA_INDEX: int = 0
"""OS device index passed to cv2.VideoCapture()."""

FRAME_WIDTH: int = 640
"""Requested capture width in pixels (cv2.CAP_PROP_FRAME_WIDTH)."""

FRAME_HEIGHT: int = 480
"""Requested capture height in pixels (cv2.CAP_PROP_FRAME_HEIGHT)."""

TARGET_FPS: int = 30
"""Desired frames per second (cv2.CAP_PROP_FPS)."""

AUTO_EXPOSURE: int = 1
"""cv2.CAP_PROP_AUTO_EXPOSURE flag value. 1 = auto-exposure enabled."""

# ---------------------------------------------------------------------------
# 2. Face Detection Settings
# ---------------------------------------------------------------------------

MIN_DETECTION_CONFIDENCE: float = 0.7
"""Minimum MediaPipe face-detection confidence threshold in [0.0, 1.0]."""

MAX_FACES: int = 1
"""Maximum number of simultaneous faces the detector tracks."""

BOUNDING_BOX_COLOR: tuple[int, int, int] = (0, 255, 0)
"""BGR colour tuple used to draw the face bounding box."""

BOUNDING_BOX_THICKNESS: int = 2
"""Stroke thickness in pixels for the face bounding box."""

TEXT_SIZE: float = 0.6
"""OpenCV font scale applied to on-frame text labels."""

# ---------------------------------------------------------------------------
# 3. Distance Estimation Settings
# ---------------------------------------------------------------------------

DEFAULT_FACE_WIDTH_CM: float = 14.3
"""Average human inter-cheekbone width in centimetres used as the known
object width in the focal-length formula:  F = (P × D) / W."""

DEFAULT_FOCAL_LENGTH: float = 615.0
"""Placeholder focal length in pixels.  Replace with a calibrated value
after running the calibration routine."""

MIN_MEASURABLE_DISTANCE_CM: float = 20.0
"""Closest valid measurement in centimetres.  Readings below this threshold
are discarded as unreliable."""

MAX_MEASURABLE_DISTANCE_CM: float = 500.0
"""Farthest valid measurement in centimetres.  Readings above this threshold
are discarded as unreliable."""

MOVING_AVERAGE_WINDOW: int = 5
"""Number of consecutive distance readings averaged to smooth output."""

# ---------------------------------------------------------------------------
# 4. Angle Estimation Settings
# ---------------------------------------------------------------------------

CAMERA_HORIZONTAL_FOV_DEG: float = 60.0
"""Horizontal field of view of the camera lens in degrees."""

CAMERA_VERTICAL_FOV_DEG: float = 45.0
"""Vertical field of view of the camera lens in degrees."""

MAX_ANGLE_DISPLAY_DEG: float = 45.0
"""Maximum angle rendered on the radar overlay in degrees.  Angles beyond
this value are clamped to the radar edge."""

# ---------------------------------------------------------------------------
# 5. Calibration Settings
# ---------------------------------------------------------------------------

CALIBRATION_DISTANCE_CM: float = 100.0
"""Known physical distance in centimetres at which the calibration target
must be placed during the calibration session."""

CALIBRATION_TOLERANCE: float = 0.1
"""Acceptable fractional deviation between individual calibration samples
and the session mean.  A value of 0.1 allows ±10 % spread."""

CALIBRATION_SAMPLES: int = 30
"""Number of frames captured and averaged to compute the calibrated focal
length during a calibration session."""

# ---------------------------------------------------------------------------
# 6. Confidence Engine Settings
# ---------------------------------------------------------------------------

CONFIDENCE_LIGHTING_WEIGHT: float = 0.25
"""Fractional contribution of scene-lighting quality to the overall
confidence score.  Must sum to 1.0 with the other three weights."""

CONFIDENCE_BLUR_WEIGHT: float = 0.25
"""Fractional contribution of image sharpness (inverse of blur) to the
overall confidence score."""

CONFIDENCE_DETECTION_STABILITY_WEIGHT: float = 0.25
"""Fractional contribution of detection-frame consistency (ratio of frames
with a valid detection in the recent window) to the confidence score."""

CONFIDENCE_FACE_SIZE_WEIGHT: float = 0.25
"""Fractional contribution of the face bounding-box area (relative to the
frame area) to the confidence score."""

CONFIDENCE_SMOOTHING_FACTOR: float = 0.3
"""Exponential moving-average alpha in [0.0, 1.0] applied to the raw
confidence score.  Higher values react faster; lower values are smoother."""

# ---------------------------------------------------------------------------
# 7. Visualization Settings
# ---------------------------------------------------------------------------

RADAR_RADIUS: int = 150
"""Radius of the radar overlay circle in pixels."""

COLOR_RADAR: tuple[int, int, int] = (0, 200, 0)
"""BGR colour used to draw radar overlay arcs and markers."""

COLOR_DASHBOARD_BG: tuple[int, int, int] = (20, 20, 20)
"""BGR background colour for the on-frame dashboard panel."""

COLOR_TEXT: tuple[int, int, int] = (255, 255, 255)
"""BGR colour for general on-frame text labels."""

COLOR_WARNING: tuple[int, int, int] = (0, 0, 255)
"""BGR colour for warning indicators (e.g. face too close)."""

COLOR_SUCCESS: tuple[int, int, int] = (0, 255, 0)
"""BGR colour for success indicators (e.g. calibration complete)."""

# ---------------------------------------------------------------------------
# 8. Logging Settings
# ---------------------------------------------------------------------------

LOG_LEVEL: str = "INFO"
"""Standard Python logging level name passed to logging.basicConfig()."""

LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""Python logging format string used by every backend logger."""

DEBUG_MODE: bool = False
"""When True, modules emit verbose debug output in addition to standard
logging.  Set to True only during local development."""

# ---------------------------------------------------------------------------
# 9. Application Metadata
# ---------------------------------------------------------------------------

APP_NAME: str = "Face Distance Estimation"
"""Human-readable display name of the application."""

APP_VERSION: str = "1.0.0"
"""Semantic version string following MAJOR.MINOR.PATCH convention."""

APP_AUTHOR: str = "Author"
"""Placeholder for the project author name or organisation."""


# ---------------------------------------------------------------------------
# Debug helper
# ---------------------------------------------------------------------------

def print_configuration() -> None:
    """Print all configuration constants grouped by section to stdout.

    Intended for development-time inspection only.  No logging framework
    needs to be configured — output goes directly to stdout via print().

    Output format
    -------------
    Each section is preceded by a banner line and followed by one
    ``  KEY = value`` line per constant.  Sections are separated by a
    blank line for readability.

    Example
    -------
    ::

        ── Camera Settings ─────────────────────────────────────────────────
          CAMERA_INDEX               = 0
          FRAME_WIDTH                = 640
          ...

        ── Face Detection Settings ──────────────────────────────────────────
          MIN_DETECTION_CONFIDENCE   = 0.7
          ...
    """
    _WIDTH: int = 68

    def _banner(title: str) -> str:
        separator: str = "─" * (_WIDTH - len(title) - 4)
        return f"── {title} {separator}"

    def _row(name: str, value: object) -> str:
        return f"  {name:<34} = {value}"

    sections: list[tuple[str, list[tuple[str, object]]]] = [
        (
            "Camera Settings",
            [
                ("CAMERA_INDEX", CAMERA_INDEX),
                ("FRAME_WIDTH", FRAME_WIDTH),
                ("FRAME_HEIGHT", FRAME_HEIGHT),
                ("TARGET_FPS", TARGET_FPS),
                ("AUTO_EXPOSURE", AUTO_EXPOSURE),
            ],
        ),
        (
            "Face Detection Settings",
            [
                ("MIN_DETECTION_CONFIDENCE", MIN_DETECTION_CONFIDENCE),
                ("MAX_FACES", MAX_FACES),
                ("BOUNDING_BOX_COLOR", BOUNDING_BOX_COLOR),
                ("BOUNDING_BOX_THICKNESS", BOUNDING_BOX_THICKNESS),
                ("TEXT_SIZE", TEXT_SIZE),
            ],
        ),
        (
            "Distance Estimation Settings",
            [
                ("DEFAULT_FACE_WIDTH_CM", DEFAULT_FACE_WIDTH_CM),
                ("DEFAULT_FOCAL_LENGTH", DEFAULT_FOCAL_LENGTH),
                ("MIN_MEASURABLE_DISTANCE_CM", MIN_MEASURABLE_DISTANCE_CM),
                ("MAX_MEASURABLE_DISTANCE_CM", MAX_MEASURABLE_DISTANCE_CM),
                ("MOVING_AVERAGE_WINDOW", MOVING_AVERAGE_WINDOW),
            ],
        ),
        (
            "Angle Estimation Settings",
            [
                ("CAMERA_HORIZONTAL_FOV_DEG", CAMERA_HORIZONTAL_FOV_DEG),
                ("CAMERA_VERTICAL_FOV_DEG", CAMERA_VERTICAL_FOV_DEG),
                ("MAX_ANGLE_DISPLAY_DEG", MAX_ANGLE_DISPLAY_DEG),
            ],
        ),
        (
            "Calibration Settings",
            [
                ("CALIBRATION_DISTANCE_CM", CALIBRATION_DISTANCE_CM),
                ("CALIBRATION_TOLERANCE", CALIBRATION_TOLERANCE),
                ("CALIBRATION_SAMPLES", CALIBRATION_SAMPLES),
            ],
        ),
        (
            "Confidence Engine Settings",
            [
                ("CONFIDENCE_LIGHTING_WEIGHT", CONFIDENCE_LIGHTING_WEIGHT),
                ("CONFIDENCE_BLUR_WEIGHT", CONFIDENCE_BLUR_WEIGHT),
                (
                    "CONFIDENCE_DETECTION_STABILITY_WEIGHT",
                    CONFIDENCE_DETECTION_STABILITY_WEIGHT,
                ),
                ("CONFIDENCE_FACE_SIZE_WEIGHT", CONFIDENCE_FACE_SIZE_WEIGHT),
                ("CONFIDENCE_SMOOTHING_FACTOR", CONFIDENCE_SMOOTHING_FACTOR),
            ],
        ),
        (
            "Visualization Settings",
            [
                ("RADAR_RADIUS", RADAR_RADIUS),
                ("COLOR_RADAR", COLOR_RADAR),
                ("COLOR_DASHBOARD_BG", COLOR_DASHBOARD_BG),
                ("COLOR_TEXT", COLOR_TEXT),
                ("COLOR_WARNING", COLOR_WARNING),
                ("COLOR_SUCCESS", COLOR_SUCCESS),
            ],
        ),
        (
            "Logging Settings",
            [
                ("LOG_LEVEL", LOG_LEVEL),
                ("LOG_FORMAT", LOG_FORMAT),
                ("DEBUG_MODE", DEBUG_MODE),
            ],
        ),
        (
            "Application Metadata",
            [
                ("APP_NAME", APP_NAME),
                ("APP_VERSION", APP_VERSION),
                ("APP_AUTHOR", APP_AUTHOR),
            ],
        ),
    ]

    print(f"\n{APP_NAME}  v{APP_VERSION}  — Active Configuration\n")
    for section_title, constants in sections:
        print(_banner(section_title))
        for name, value in constants:
            print(_row(name, value))
        print()
