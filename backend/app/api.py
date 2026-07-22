"""
api.py — Backend orchestration layer for the Face Distance Estimation backend.

This module exposes a single public class:

* ``FaceDistanceAPI`` — coordinates the camera, face detector, distance
  estimator, angle estimator, and camera calibrator into a cohesive
  processing pipeline.

Responsibilities
----------------
* Initialise and own exactly one instance of each component.
* Open the camera at startup; raise ``RuntimeError`` on failure.
* Process frames through the full detection → estimation pipeline and return
  structured result dictionaries.
* Expose a single-frame calibration workflow.
* Release all resources cleanly on shutdown; safe to call multiple times.

Out of scope
------------
This module does **not** create a FastAPI application, define HTTP routes,
configure Uvicorn, implement WebSocket streaming, perform visualisation,
act as a CLI entry point, or configure logging.  Those responsibilities
belong to ``main.py``.

Logging is intentionally **not** configured here.  The application entry
point (``main.py``) is responsible for calling ``logging.basicConfig()``.

Usage
-----
::

    from app.api import FaceDistanceAPI

    api = FaceDistanceAPI()

    result = api.process_frame()
    # {'success': True, 'face_detected': True, 'distance_cm': 82.4, ...}

    focal_length = api.calibrate(known_distance_cm=100.0)

    api.shutdown()
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from numpy.typing import NDArray

from app.angle import AngleEstimator
from app.calibration import CameraCalibrator
from app.camera import Camera
from app.detector import FaceDetection, FaceDetector
from app.distance import DistanceEstimator

# ---------------------------------------------------------------------------
# Module logger — configuration delegated to the application entry point
# ---------------------------------------------------------------------------

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FaceDistanceAPI
# ---------------------------------------------------------------------------


class FaceDistanceAPI:
    """Orchestrates camera, detection, and estimation components.

    ``FaceDistanceAPI`` owns the full lifecycle of one ``Camera``,
    ``FaceDetector``, ``DistanceEstimator``, ``AngleEstimator``, and
    ``CameraCalibrator``.  The camera is opened during ``__init__``; all
    resources are released by :meth:`shutdown`.

    The class deliberately exposes a narrow, dictionary-based interface so
    that higher-level layers (FastAPI routes, WebSocket handlers, CLIs) can
    consume results without importing any component directly.

    Thread safety
    -------------
    This class is **not** thread-safe.  Each concurrent user should hold its
    own instance, or external locking must be applied.

    Example
    -------
    ::

        api = FaceDistanceAPI()
        try:
            while True:
                result = api.process_frame()
                if result["success"] and result["face_detected"]:
                    print(result["distance_cm"], result["angle_deg"])
        finally:
            api.shutdown()
    """

    def __init__(self) -> None:
        """Initialise all backend components and open the camera.

        Creates exactly one instance of:

        * :class:`~app.camera.Camera` — opened immediately via ``start()``.
        * :class:`~app.detector.FaceDetector` — MediaPipe model loaded.
        * :class:`~app.distance.DistanceEstimator` — moving-average buffer
          initialised.
        * :class:`~app.angle.AngleEstimator` — stateless; config validated.
        * :class:`~app.calibration.CameraCalibrator` — default focal length
          set.

        Raises
        ------
        RuntimeError
            If the camera cannot be opened (device unavailable, index invalid,
            or already in use by another process), or if any component fails
            to initialise due to misconfigured constants.
        """
        self._camera = Camera()
        self._detector = FaceDetector()
        self._distance_estimator = DistanceEstimator()
        self._angle_estimator = AngleEstimator()
        self._calibrator = CameraCalibrator()

        self._is_shutdown: bool = False

        try:
            self._camera.start()
        except RuntimeError as exc:
            # Release the detector before re-raising so we don't leak
            # MediaPipe resources when the camera fails to open.
            self._detector.close()
            raise RuntimeError(
                f"FaceDistanceAPI failed to start: camera could not be opened. "
                f"Details: {exc}"
            ) from exc

        logger.info("FaceDistanceAPI initialised — all components ready.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_frame(self) -> dict[str, Any]:
        """Capture one frame and run the full detection-estimation pipeline.

        Pipeline steps
        --------------
        1. Read one frame from the camera.
        2. If capture fails, return an error result dictionary.
        3. Detect faces in the frame.
        4. If no face is detected, return a no-face result dictionary.
        5. Use **only the first** detected face.
        6. Estimate distance (cm) via :class:`~app.distance.DistanceEstimator`.
        7. Estimate horizontal angle (°) via :class:`~app.angle.AngleEstimator`.
        8. Return a structured result dictionary.

        Returns
        -------
        dict[str, Any]
            One of three shapes:

            **Capture failure**::

                {
                    "success": False,
                    "error": "Failed to capture frame."
                }

            **No face detected**::

                {
                    "success": True,
                    "face_detected": False
                }

            **Face detected**::

                {
                    "success": True,
                    "face_detected": True,
                    "distance_cm": float,
                    "angle_deg": float,
                    "bbox": {
                        "x": int,
                        "y": int,
                        "width": int,
                        "height": int
                    },
                    "detection_confidence": float
                }

        Notes
        -----
        * Unexpected internal errors (estimation failures) are logged and
          re-raised rather than silently swallowed, so the caller can decide
          on retry or abort behaviour.
        * This method is safe to call in a tight loop; the distance estimator
          maintains its own moving-average history across calls.
        """
        success, frame = self._camera.read()

        if not success or frame is None:
            logger.warning("process_frame() — frame capture failed.")
            return {"success": False, "error": "Failed to capture frame."}

        detections: list[FaceDetection] = self._detector.detect(frame)

        if not detections:
            logger.debug("process_frame() — no face detected.")
            return {"success": True, "face_detected": False}

        face: FaceDetection = detections[0]
        frame_width: int = frame.shape[1]

        distance_cm: float = self._distance_estimator.estimate(face)
        angle_deg: float = self._angle_estimator.estimate(face, frame_width)

        result: dict[str, Any] = {
            "success": True,
            "face_detected": True,
            "distance_cm": float(distance_cm),
            "angle_deg": float(angle_deg),
            "bbox": {
                "x": int(face.bbox_x),
                "y": int(face.bbox_y),
                "width": int(face.bbox_width),
                "height": int(face.bbox_height),
            },
            "detection_confidence": float(face.confidence),
        }

        logger.debug(
            "process_frame() — distance=%.2f cm, angle=%.2f°, "
            "confidence=%.3f, bbox=(%d, %d, %d, %d).",
            distance_cm,
            angle_deg,
            face.confidence,
            face.bbox_x,
            face.bbox_y,
            face.bbox_width,
            face.bbox_height,
        )

        return result

    def calibrate(self, known_distance_cm: float) -> float:
        """Calibrate the focal length using a single captured frame.

        Captures one frame, detects the first face, and uses
        :meth:`~app.calibration.CameraCalibrator.calculate_focal_length`
        to derive and store a calibrated focal length.

        The calibrated focal length is stored in the ``CameraCalibrator``
        instance owned by this class.  Integration of the new value into
        the ``DistanceEstimator`` is intentionally deferred to a later
        implementation step.

        Parameters
        ----------
        known_distance_cm : float
            The precise physical distance in centimetres between the camera
            lens and the subject's face at the moment of calibration capture.
            Must be strictly positive.

        Returns
        -------
        float
            The newly calibrated focal length in pixels, as returned by
            :meth:`~app.calibration.CameraCalibrator.calculate_focal_length`.

        Raises
        ------
        RuntimeError
            If the camera fails to capture a frame, or if no face is
            detected in the captured frame.
        ValueError
            If *known_distance_cm* is zero or negative (propagated from
            :class:`~app.calibration.CameraCalibrator`).
        """
        success, frame = self._camera.read()

        if not success or frame is None:
            logger.error(
                "calibrate() — frame capture failed; "
                "cannot perform calibration."
            )
            raise RuntimeError(
                "Calibration failed: could not capture a frame from the camera."
            )

        detections: list[FaceDetection] = self._detector.detect(frame)

        if not detections:
            logger.error(
                "calibrate() — no face detected in calibration frame; "
                "known_distance_cm=%.2f cm.",
                known_distance_cm,
            )
            raise RuntimeError(
                "Calibration failed: no face was detected in the captured frame. "
                "Ensure the subject is visible and well-lit, then retry."
            )

        face: FaceDetection = detections[0]
        focal_length: float = self._calibrator.calculate_focal_length(
            face=face,
            known_distance_cm=known_distance_cm,
        )

        logger.info(
            "calibrate() — calibration completed, "
            "known_distance=%.2f cm, focal_length=%.4f px.",
            known_distance_cm,
            focal_length,
        )

        return focal_length

    def shutdown(self) -> None:
        """Release all backend resources.

        Calls ``Camera.stop()`` and ``FaceDetector.close()`` to release the
        webcam device and MediaPipe model memory.  Safe to call multiple
        times — subsequent calls after the first are no-ops.

        Returns
        -------
        None
        """
        if self._is_shutdown:
            logger.debug("shutdown() called on an already-shut-down instance; skipping.")
            return

        self._camera.stop()
        self._detector.close()
        self._is_shutdown = True

        logger.info("FaceDistanceAPI shutdown completed — all resources released.")
