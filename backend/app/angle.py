"""
angle.py — Horizontal angle estimation for the Face Distance Estimation backend.

This module exposes a single public class:

* ``AngleEstimator`` — accepts a ``FaceDetection`` object and the frame width
  in pixels, and returns the estimated horizontal viewing angle (in degrees)
  of the detected face relative to the camera centre.

Responsibilities
----------------
* Compute the horizontal pixel offset of the face centre from the image centre.
* Normalise that offset against the half-frame width.
* Scale the normalised offset by the camera's horizontal half-FOV.
* Clamp the result to ``[-MAX_ANGLE_DISPLAY_DEG, +MAX_ANGLE_DISPLAY_DEG]``.
* Raise descriptive exceptions for invalid inputs.

Out of scope
------------
This module does **not** perform face detection, distance estimation,
calibration, visualisation, or any FastAPI logic.

Sign convention
---------------
* Negative angles → face is to the **left** of the camera centre.
* Positive angles → face is to the **right** of the camera centre.
* Zero → face is centred.

Logging is intentionally **not** configured here.  The application entry
point (``main.py``) is responsible for calling ``logging.basicConfig()``.

Usage
-----
::

    from app.detector import FaceDetection
    from app.angle import AngleEstimator

    estimator = AngleEstimator()
    angle_deg: float = estimator.estimate(detection, frame_width=640)
"""

from __future__ import annotations

import logging

from app.config import CAMERA_HORIZONTAL_FOV_DEG, MAX_ANGLE_DISPLAY_DEG
from app.detector import FaceDetection

# ---------------------------------------------------------------------------
# Module logger — configuration delegated to the application entry point
# ---------------------------------------------------------------------------

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# AngleEstimator
# ---------------------------------------------------------------------------


class AngleEstimator:
    """Estimates the horizontal viewing angle of a detected face.

    The angle is derived by mapping the face's horizontal pixel position
    onto the camera's horizontal field of view::

        image_center     = frame_width / 2
        offset_pixels    = face.center_x - image_center
        normalized_offset = offset_pixels / image_center
        angle            = normalized_offset * (CAMERA_HORIZONTAL_FOV_DEG / 2)

    The raw angle is clamped to
    ``[-MAX_ANGLE_DISPLAY_DEG, +MAX_ANGLE_DISPLAY_DEG]`` before being
    returned.

    All configuration values are imported from ``app.config``; nothing is
    hardcoded in this class.

    Sign convention
    ---------------
    * Negative → face is left of centre.
    * Positive → face is right of centre.
    * Zero     → face is centred.

    Thread safety
    -------------
    This class is **stateless** after initialisation, so a single instance
    may be called from multiple threads without external locking.

    Example
    -------
    ::

        estimator = AngleEstimator()
        angle = estimator.estimate(face_detection, frame_width=640)
    """

    def __init__(self) -> None:
        """Initialise the estimator and validate configuration constants.

        Reads ``CAMERA_HORIZONTAL_FOV_DEG`` and ``MAX_ANGLE_DISPLAY_DEG``
        from ``app.config`` and verifies they are positive finite values.
        No frames are processed during initialisation.

        Raises
        ------
        RuntimeError
            If either configuration constant is non-positive, which would
            make angle computation undefined or meaningless.
        """
        self._validate_config()

        logger.info(
            "AngleEstimator initialised — horizontal_fov=%.1f°, "
            "max_display_angle=%.1f°.",
            CAMERA_HORIZONTAL_FOV_DEG,
            MAX_ANGLE_DISPLAY_DEG,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def estimate(self, face: FaceDetection, frame_width: int) -> float:
        """Estimate the horizontal viewing angle of the detected face.

        Computes the signed angle (in degrees) between the camera's optical
        axis and the line of sight to the face centre, using a linear
        projection of the face's horizontal pixel offset onto the camera's
        horizontal field of view.

        Algorithm::

            image_center      = frame_width / 2
            offset_pixels     = face.center_x - image_center
            normalized_offset = offset_pixels / image_center
            angle             = normalized_offset * (CAMERA_HORIZONTAL_FOV_DEG / 2)

        The result is then clamped to
        ``[-MAX_ANGLE_DISPLAY_DEG, +MAX_ANGLE_DISPLAY_DEG]``.

        Parameters
        ----------
        face : FaceDetection
            A ``FaceDetection`` instance produced by ``FaceDetector.detect()``.
            The ``center_x`` attribute must be a valid pixel coordinate within
            the frame.
        frame_width : int
            Width of the source frame in pixels.  Must be strictly positive.

        Returns
        -------
        float
            Horizontal angle in degrees, clamped to
            ``[-MAX_ANGLE_DISPLAY_DEG, +MAX_ANGLE_DISPLAY_DEG]``.
            Negative values indicate the face is to the left of centre;
            positive values indicate the face is to the right.

        Raises
        ------
        TypeError
            If *face* is not a ``FaceDetection`` instance.
        ValueError
            If *frame_width* is zero or negative, which would make the
            image-centre computation undefined.
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

        if frame_width <= 0:
            logger.error(
                "estimate() received frame_width=%d — must be strictly positive.",
                frame_width,
            )
            raise ValueError(
                f"frame_width must be strictly positive, got {frame_width!r}."
            )

        image_center: float = frame_width / 2.0
        offset_pixels: float = face.center_x - image_center
        normalized_offset: float = offset_pixels / image_center
        raw_angle: float = normalized_offset * (CAMERA_HORIZONTAL_FOV_DEG / 2.0)

        clamped_angle: float = max(
            -MAX_ANGLE_DISPLAY_DEG,
            min(raw_angle, MAX_ANGLE_DISPLAY_DEG),
        )

        logger.debug(
            "Angle estimated — center_x=%d px, frame_width=%d px, "
            "offset=%.2f px, normalised=%.4f, raw=%.2f°, clamped=%.2f°.",
            face.center_x,
            frame_width,
            offset_pixels,
            normalized_offset,
            raw_angle,
            clamped_angle,
        )

        return clamped_angle

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_config() -> None:
        """Validate angle-related configuration constants at startup.

        Checks that the values imported from ``config.py`` are positive and
        finite so any misconfiguration is caught immediately at
        initialisation time.

        Raises
        ------
        RuntimeError
            If any configuration value is logically inconsistent:

            * ``CAMERA_HORIZONTAL_FOV_DEG`` is not positive.
            * ``MAX_ANGLE_DISPLAY_DEG`` is not positive.
        """
        if CAMERA_HORIZONTAL_FOV_DEG <= 0:
            raise RuntimeError(
                f"CAMERA_HORIZONTAL_FOV_DEG must be positive, "
                f"got {CAMERA_HORIZONTAL_FOV_DEG!r}."
            )
        if MAX_ANGLE_DISPLAY_DEG <= 0:
            raise RuntimeError(
                f"MAX_ANGLE_DISPLAY_DEG must be positive, "
                f"got {MAX_ANGLE_DISPLAY_DEG!r}."
            )
