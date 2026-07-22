"""
calibration.py — Camera focal-length calibration for the Face Distance Estimation backend.

This module exposes a single public class:

* ``CameraCalibrator`` — computes and stores the camera focal length using a
  known-distance calibration procedure based on the pinhole camera model.

Responsibilities
----------------
* Calculate a calibrated focal length from a ``FaceDetection`` taken at a
  known physical distance.
* Store the active focal length (initialised to ``DEFAULT_FOCAL_LENGTH``).
* Allow external code to read, override, or reset the stored focal length.
* Raise descriptive exceptions for invalid inputs.

Out of scope
------------
This module does **not** perform face detection, distance estimation, angle
estimation, visualisation, or any FastAPI logic.

Pinhole camera model
--------------------
The focal length is derived from the standard formula::

    focal_length = (known_distance_cm * face.bbox_width) / DEFAULT_FACE_WIDTH_CM

where ``DEFAULT_FACE_WIDTH_CM`` is the assumed average inter-cheekbone width
of a human face, imported from ``app.config``.

Logging is intentionally **not** configured here.  The application entry
point (``main.py``) is responsible for calling ``logging.basicConfig()``.

Usage
-----
::

    from app.detector import FaceDetection
    from app.calibration import CameraCalibrator

    calibrator = CameraCalibrator()

    # Compute and store focal length from a live detection
    focal_length = calibrator.calculate_focal_length(
        face=detection,
        known_distance_cm=100.0,
    )

    # Read back the stored value
    fl = calibrator.get_focal_length()

    # Override with a pre-computed value
    calibrator.set_focal_length(620.0)

    # Restore factory default
    calibrator.reset()
"""

from __future__ import annotations

import logging

from app.config import DEFAULT_FACE_WIDTH_CM, DEFAULT_FOCAL_LENGTH
from app.detector import FaceDetection

# ---------------------------------------------------------------------------
# Module logger — configuration delegated to the application entry point
# ---------------------------------------------------------------------------

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CameraCalibrator
# ---------------------------------------------------------------------------


class CameraCalibrator:
    """Computes and stores the camera focal length via a known-distance procedure.

    On construction the active focal length is set to ``DEFAULT_FOCAL_LENGTH``
    (from ``app.config``).  Calling :meth:`calculate_focal_length` with a
    ``FaceDetection`` taken at a known physical distance replaces the stored
    value with the freshly calibrated result.

    The stored focal length can also be overridden directly via
    :meth:`set_focal_length` and read back at any time via
    :meth:`get_focal_length`.  :meth:`reset` restores the factory default.

    All configuration values are imported from ``app.config``; nothing is
    hardcoded in this class.

    Thread safety
    -------------
    This class is **not** thread-safe.  External locking is required if the
    same instance is accessed from multiple threads.

    Example
    -------
    ::

        calibrator = CameraCalibrator()
        fl = calibrator.calculate_focal_length(detection, known_distance_cm=100.0)
        calibrator.reset()
    """

    def __init__(self) -> None:
        """Initialise the calibrator with the default focal length.

        Sets the internal focal-length store to ``DEFAULT_FOCAL_LENGTH``
        imported from ``config.py``.  No frames are processed during
        initialisation.

        Raises
        ------
        RuntimeError
            If ``DEFAULT_FOCAL_LENGTH`` or ``DEFAULT_FACE_WIDTH_CM`` imported
            from ``config.py`` are non-positive, indicating a misconfigured
            environment.
        """
        self._validate_config()

        self._focal_length: float = DEFAULT_FOCAL_LENGTH

        logger.info(
            "CameraCalibrator initialised — focal_length=%.2f px, "
            "face_width=%.2f cm.",
            self._focal_length,
            DEFAULT_FACE_WIDTH_CM,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_focal_length(
        self,
        face: FaceDetection,
        known_distance_cm: float,
    ) -> float:
        """Calculate and store the focal length from a calibration detection.

        Uses the pinhole camera equation to derive the focal length from a
        ``FaceDetection`` captured at a precisely known physical distance::

            focal_length = (known_distance_cm * face.bbox_width)
                           / DEFAULT_FACE_WIDTH_CM

        The computed value is stored internally so that it is immediately
        available via :meth:`get_focal_length`.

        Parameters
        ----------
        face : FaceDetection
            A ``FaceDetection`` instance produced by ``FaceDetector.detect()``
            while the subject stands at exactly *known_distance_cm* from the
            camera.  ``face.bbox_width`` must be strictly positive.
        known_distance_cm : float
            The measured physical distance in centimetres between the camera
            lens and the subject's face at the time of capture.  Must be
            strictly positive.

        Returns
        -------
        float
            The calculated focal length in pixels.  This value is also stored
            internally and replaces any previously stored focal length.

        Raises
        ------
        TypeError
            If *face* is not a ``FaceDetection`` instance.
        ValueError
            If ``face.bbox_width`` is zero or negative, or if
            *known_distance_cm* is zero or negative.
        """
        if not isinstance(face, FaceDetection):
            logger.error(
                "calculate_focal_length() received an invalid input type: "
                "%s — expected FaceDetection.",
                type(face).__name__,
            )
            raise TypeError(
                f"calculate_focal_length() expects a FaceDetection instance, "
                f"got {type(face).__name__!r} instead."
            )

        if face.bbox_width <= 0:
            logger.error(
                "calculate_focal_length() received bbox_width=%d — "
                "must be strictly positive.",
                face.bbox_width,
            )
            raise ValueError(
                f"face.bbox_width must be strictly positive, "
                f"got {face.bbox_width!r}."
            )

        if known_distance_cm <= 0:
            logger.error(
                "calculate_focal_length() received known_distance_cm=%.4f — "
                "must be strictly positive.",
                known_distance_cm,
            )
            raise ValueError(
                f"known_distance_cm must be strictly positive, "
                f"got {known_distance_cm!r}."
            )

        focal_length: float = (
            known_distance_cm * face.bbox_width
        ) / DEFAULT_FACE_WIDTH_CM

        self._focal_length = focal_length

        logger.info(
            "Calibration completed — known_distance=%.2f cm, "
            "bbox_width=%d px, focal_length=%.4f px.",
            known_distance_cm,
            face.bbox_width,
            focal_length,
        )

        return focal_length

    def set_focal_length(self, focal_length: float) -> None:
        """Override the stored focal length with an externally supplied value.

        Use this when a previously calibrated focal length has been persisted
        (e.g. loaded from a configuration file) and should be restored without
        running the full calibration procedure again.

        Parameters
        ----------
        focal_length : float
            The focal length in pixels to store.  Must be strictly positive.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If *focal_length* is zero or negative, which would produce
            physically meaningless distance estimates downstream.
        """
        if focal_length <= 0:
            logger.error(
                "set_focal_length() received focal_length=%.4f — "
                "must be strictly positive.",
                focal_length,
            )
            raise ValueError(
                f"focal_length must be strictly positive, got {focal_length!r}."
            )

        previous: float = self._focal_length
        self._focal_length = focal_length

        logger.info(
            "Focal length updated — previous=%.4f px, new=%.4f px.",
            previous,
            focal_length,
        )

    def get_focal_length(self) -> float:
        """Return the currently stored focal length in pixels.

        Returns the value set by the most recent call to
        :meth:`calculate_focal_length` or :meth:`set_focal_length`, or
        ``DEFAULT_FOCAL_LENGTH`` if neither has been called (or after
        :meth:`reset`).

        Returns
        -------
        float
            The active focal length in pixels.  Always strictly positive.
        """
        return self._focal_length

    def reset(self) -> None:
        """Restore the focal length to the factory default.

        Sets the internal focal length back to ``DEFAULT_FOCAL_LENGTH``
        imported from ``config.py``, discarding any calibrated or manually
        set value.

        Returns
        -------
        None
        """
        previous: float = self._focal_length
        self._focal_length = DEFAULT_FOCAL_LENGTH

        logger.info(
            "CameraCalibrator reset — focal_length restored from "
            "%.4f px to default %.4f px.",
            previous,
            DEFAULT_FOCAL_LENGTH,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_config() -> None:
        """Validate calibration-related configuration constants at startup.

        Checks that the values imported from ``config.py`` are positive so
        any misconfiguration is surfaced immediately at initialisation time
        rather than producing silent errors during calibration.

        Raises
        ------
        RuntimeError
            If any configuration value is logically inconsistent:

            * ``DEFAULT_FOCAL_LENGTH`` is not positive.
            * ``DEFAULT_FACE_WIDTH_CM`` is not positive.
        """
        if DEFAULT_FOCAL_LENGTH <= 0:
            raise RuntimeError(
                f"DEFAULT_FOCAL_LENGTH must be positive, "
                f"got {DEFAULT_FOCAL_LENGTH!r}."
            )
        if DEFAULT_FACE_WIDTH_CM <= 0:
            raise RuntimeError(
                f"DEFAULT_FACE_WIDTH_CM must be positive, "
                f"got {DEFAULT_FACE_WIDTH_CM!r}."
            )
