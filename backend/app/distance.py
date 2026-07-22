"""
distance.py — Distance estimation for the Face Distance Estimation backend.

This module exposes a single public class:

* ``DistanceEstimator`` — accepts a ``FaceDetection`` object and returns the
  estimated distance (in centimetres) between the webcam and the detected face,
  smoothed via a configurable moving-average window and clamped to a valid
  measurement range.

Responsibilities
----------------
* Apply the pinhole camera model to convert bounding-box width to distance.
* Smooth successive estimates with a fixed-length moving-average window.
* Clamp the final value to the configured measurable range.
* Raise descriptive exceptions for invalid inputs.

Out of scope
------------
This module does **not** perform face detection, angle calculation,
calibration, visualisation, or any FastAPI logic.

Logging is intentionally **not** configured here.  The application entry
point (``main.py``) is responsible for calling ``logging.basicConfig()``.

Usage
-----
::

    from app.detector import FaceDetection
    from app.distance import DistanceEstimator

    estimator = DistanceEstimator()
    distance_cm: float = estimator.estimate(detection)
    estimator.reset()
"""

from __future__ import annotations

import logging
from collections import deque
from typing import Deque

from app.config import (
    DEFAULT_FACE_WIDTH_CM,
    DEFAULT_FOCAL_LENGTH,
    MAX_MEASURABLE_DISTANCE_CM,
    MIN_MEASURABLE_DISTANCE_CM,
    MOVING_AVERAGE_WINDOW,
)
from app.detector import FaceDetection

# ---------------------------------------------------------------------------
# Module logger — configuration delegated to the application entry point
# ---------------------------------------------------------------------------

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DistanceEstimator
# ---------------------------------------------------------------------------


class DistanceEstimator:
    """Estimates the distance between the webcam and a detected face.

    Uses the pinhole camera equation to convert the pixel width of a face
    bounding box into a physical distance in centimetres::

        distance = (DEFAULT_FACE_WIDTH_CM * DEFAULT_FOCAL_LENGTH) / bbox_width

    Successive raw estimates are stored in a fixed-length moving-average
    window (``MOVING_AVERAGE_WINDOW``).  The smoothed mean is then clamped
    to ``[MIN_MEASURABLE_DISTANCE_CM, MAX_MEASURABLE_DISTANCE_CM]`` before
    being returned to the caller.

    All configuration values are imported from ``app.config``; nothing is
    hardcoded in this class.

    Thread safety
    -------------
    This class is **not** thread-safe.  External locking is required if the
    same instance is accessed from multiple threads.

    Example
    -------
    ::

        estimator = DistanceEstimator()
        cm = estimator.estimate(face_detection)
        estimator.reset()
    """

    def __init__(self) -> None:
        """Initialise the estimator and its internal history buffer.

        Creates an empty deque with a maximum length of
        ``MOVING_AVERAGE_WINDOW`` (imported from ``config.py``).  No frames
        are processed during initialisation.

        Raises
        ------
        RuntimeError
            If the configuration constants imported from ``config.py`` are
            logically inconsistent (e.g. ``MIN > MAX`` measurable distance,
            or a non-positive window size).
        """
        self._validate_config()

        self._history: Deque[float] = deque(maxlen=MOVING_AVERAGE_WINDOW)

        logger.info(
            "DistanceEstimator initialised — focal_length=%.1f px, "
            "face_width=%.1f cm, window=%d, range=[%.1f, %.1f] cm.",
            DEFAULT_FOCAL_LENGTH,
            DEFAULT_FACE_WIDTH_CM,
            MOVING_AVERAGE_WINDOW,
            MIN_MEASURABLE_DISTANCE_CM,
            MAX_MEASURABLE_DISTANCE_CM,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def estimate(self, face: FaceDetection) -> float:
        """Estimate the distance to the detected face in centimetres.

        Applies the pinhole camera equation to the bounding-box width of
        *face*, appends the raw distance to the moving-average history, and
        returns the smoothed, clamped result.

        Formula::

            raw_distance = (DEFAULT_FACE_WIDTH_CM * DEFAULT_FOCAL_LENGTH)
                           / face.bbox_width

        The returned value is the arithmetic mean of all values currently
        stored in the history window, clamped to
        ``[MIN_MEASURABLE_DISTANCE_CM, MAX_MEASURABLE_DISTANCE_CM]``.

        Parameters
        ----------
        face : FaceDetection
            A ``FaceDetection`` instance produced by ``FaceDetector.detect()``.
            The ``bbox_width`` attribute must be a strictly positive integer.

        Returns
        -------
        float
            Smoothed distance estimate in centimetres, clamped to the
            configured measurable range.

        Raises
        ------
        TypeError
            If *face* is not a ``FaceDetection`` instance.
        ValueError
            If ``face.bbox_width`` is zero or negative, which would produce
            a division-by-zero or physically meaningless result.
        """
        if not isinstance(face, FaceDetection):
            logger.error(
                "estimate() received an invalid input type: %s — expected FaceDetection.",
                type(face).__name__,
            )
            raise TypeError(
                f"estimate() expects a FaceDetection instance, "
                f"got {type(face).__name__!r} instead."
            )

        if face.bbox_width <= 0:
            logger.error(
                "estimate() received bbox_width=%d — must be strictly positive.",
                face.bbox_width,
            )
            raise ValueError(
                f"face.bbox_width must be strictly positive, "
                f"got {face.bbox_width!r}."
            )

        raw_distance: float = (
            DEFAULT_FACE_WIDTH_CM * DEFAULT_FOCAL_LENGTH
        ) / face.bbox_width

        self._history.append(raw_distance)

        smoothed: float = sum(self._history) / len(self._history)

        clamped: float = max(
            MIN_MEASURABLE_DISTANCE_CM,
            min(smoothed, MAX_MEASURABLE_DISTANCE_CM),
        )

        logger.debug(
            "Distance estimated — bbox_width=%d px, raw=%.2f cm, "
            "smoothed=%.2f cm, clamped=%.2f cm.",
            face.bbox_width,
            raw_distance,
            smoothed,
            clamped,
        )

        return clamped

    def reset(self) -> None:
        """Clear all stored distance history.

        Empties the internal moving-average window so that the next call to
        :meth:`estimate` begins with a fresh history.  Useful when a new
        measurement session starts or a tracked face is lost and reacquired.

        Returns
        -------
        None
        """
        self._history.clear()
        logger.info("DistanceEstimator history reset — window cleared.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_config() -> None:
        """Validate the distance-related configuration constants at startup.

        Checks that the values imported from ``config.py`` are logically
        consistent so any misconfiguration is caught immediately rather than
        producing silent, hard-to-diagnose errors at runtime.

        Raises
        ------
        RuntimeError
            If any configuration value is logically inconsistent:

            * ``MOVING_AVERAGE_WINDOW`` is not a positive integer.
            * ``DEFAULT_FOCAL_LENGTH`` is not positive.
            * ``DEFAULT_FACE_WIDTH_CM`` is not positive.
            * ``MIN_MEASURABLE_DISTANCE_CM`` >= ``MAX_MEASURABLE_DISTANCE_CM``.
        """
        if not isinstance(MOVING_AVERAGE_WINDOW, int) or MOVING_AVERAGE_WINDOW < 1:
            raise RuntimeError(
                f"MOVING_AVERAGE_WINDOW must be a positive integer, "
                f"got {MOVING_AVERAGE_WINDOW!r}."
            )
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
        if MIN_MEASURABLE_DISTANCE_CM >= MAX_MEASURABLE_DISTANCE_CM:
            raise RuntimeError(
                f"MIN_MEASURABLE_DISTANCE_CM ({MIN_MEASURABLE_DISTANCE_CM}) "
                f"must be less than MAX_MEASURABLE_DISTANCE_CM "
                f"({MAX_MEASURABLE_DISTANCE_CM})."
            )
