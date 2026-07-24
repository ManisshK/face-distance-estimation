"""
api.py — Backend orchestration layer for the Face Distance Estimation backend.

Architecture — shared pipeline
-------------------------------
A single background thread (``_pipeline_thread``) owns the entire
capture → detect → estimate → annotate → encode loop.  It runs at the
camera's native frame rate and writes its output into two thread-safe
slots protected by a ``threading.Lock``:

* ``_frame_state`` — the latest :class:`FrameState` snapshot consumed by
  ``process_frame()`` and ``calibrate()``.
* ``_jpeg_bytes``  — the latest annotated JPEG bytes consumed by
  ``read_annotated_frame()``.

Both public methods are now **pure readers** — they never touch the camera
or the detector.  This eliminates the duplicate-read / duplicate-detect
problem and ensures the video stream and the metrics endpoint share exactly
the same detection result for every physical camera frame.

Stabilisation
-------------
* **Confidence gate** — raw detections below ``STREAM_CONFIDENCE_THRESHOLD``
  are discarded as noise before any smoothing or estimation takes place.
* **Grace-period hold** — when detection is lost the previous bounding box
  and estimates are retained for up to ``DETECTION_GRACE_FRAMES`` frames
  before being cleared.  This prevents single-frame blink artefacts.
* **Bounding-box EMA** — the four bbox coordinates are smoothed with an
  exponential moving average controlled by ``BBOX_SMOOTHING_ALPHA``.
  alpha=1.0 means no smoothing; alpha=0.5 is the default.

All thresholds and alphas are imported from ``config.py`` — nothing is
hardcoded.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import cv2
import numpy as np
from numpy.typing import NDArray

from app.angle import AngleEstimator
from app.calibration import CameraCalibrator
from app.camera import Camera
from app.config import (
    BBOX_SMOOTHING_ALPHA,
    BOUNDING_BOX_COLOR,
    BOUNDING_BOX_THICKNESS,
    COLOR_TEXT,
    DETECTION_GRACE_FRAMES,
    STREAM_CONFIDENCE_THRESHOLD,
    TEXT_SIZE,
)
from app.detector import FaceDetection, FaceDetector
from app.distance import DistanceEstimator

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal state dataclass
# ---------------------------------------------------------------------------

@dataclass
class FrameState:
    """Snapshot produced by the pipeline thread and consumed by endpoints.

    All fields reflect the most recent completed pipeline iteration.
    The dataclass is replaced atomically under the pipeline lock — readers
    always see a consistent snapshot.
    """

    # Camera health
    capture_ok: bool = False

    # Detection result (None when no face is present after grace period)
    face: Optional[FaceDetection] = None

    # Smoothed bbox coordinates (floats; rounded to int when used for drawing)
    smooth_x: float = 0.0
    smooth_y: float = 0.0
    smooth_w: float = 0.0
    smooth_h: float = 0.0

    # Estimation results
    distance_cm: float = 0.0
    angle_deg: float = 0.0

    # Counters
    grace_counter: int = 0          # frames elapsed since last valid detection
    frame_width: int = 640


# ---------------------------------------------------------------------------
# FaceDistanceAPI
# ---------------------------------------------------------------------------

class FaceDistanceAPI:
    """Orchestrates camera, detection, and estimation via a shared pipeline.

    A single background thread runs the full capture → detect → estimate →
    annotate → encode loop continuously.  The two public endpoint methods
    (``process_frame`` and ``read_annotated_frame``) are pure readers that
    return the latest cached result without touching hardware.

    Thread safety
    -------------
    ``_frame_state`` and ``_jpeg_bytes`` are both guarded by ``_lock``.
    The pipeline thread holds the lock only for the brief copy-write at the
    end of each iteration; readers hold it only long enough to copy the
    reference.  OpenCV and detector calls happen outside the lock.
    """

    def __init__(self) -> None:
        """Initialise all components and start the pipeline background thread."""
        self._camera = Camera()
        self._detector = FaceDetector()
        self._distance_estimator = DistanceEstimator()
        self._angle_estimator = AngleEstimator()
        self._calibrator = CameraCalibrator()

        try:
            self._camera.start()
        except RuntimeError as exc:
            self._detector.close()
            raise RuntimeError(
                f"FaceDistanceAPI failed to start: camera could not be opened. "
                f"Details: {exc}"
            ) from exc

        # Shared state protected by _lock
        self._lock = threading.Lock()
        self._frame_state: FrameState = FrameState()
        self._jpeg_bytes: Optional[bytes] = None

        # Pipeline control
        self._stop_event = threading.Event()
        self._is_shutdown = False

        self._pipeline_thread = threading.Thread(
            target=self._pipeline_loop,
            name="face-pipeline",
            daemon=True,
        )
        self._pipeline_thread.start()

        logger.info("FaceDistanceAPI initialised — pipeline thread started.")

    # ------------------------------------------------------------------
    # Pipeline thread
    # ------------------------------------------------------------------

    def _pipeline_loop(self) -> None:
        """Main loop running in the background thread.

        Each iteration:
        1. Read one frame from the camera.
        2. Run YuNet face detection.
        3. Apply confidence gate and grace-period logic.
        4. If a valid (possibly held) face exists:
           a. Apply EMA smoothing to the bounding box.
           b. Estimate distance and angle.
           c. Draw the annotated overlay onto the frame.
        5. JPEG-encode the annotated frame.
        6. Write both ``_frame_state`` and ``_jpeg_bytes`` under the lock.

        The loop runs as fast as the camera allows; no artificial sleep is
        added here.  The camera's own hardware timing (TARGET_FPS in config)
        limits throughput naturally.
        """
        # Persistent smoothed bbox — lives across iterations
        smooth_x: float = 0.0
        smooth_y: float = 0.0
        smooth_w: float = 0.0
        smooth_h: float = 0.0
        initialized: bool = False   # True once the EMA has a seed value
        grace_counter: int = 0
        last_face: Optional[FaceDetection] = None

        while not self._stop_event.is_set():
            # ── 1. Capture ──────────────────────────────────────────────
            capture_ok, frame = self._camera.read()

            if not capture_ok or frame is None:
                logger.warning("_pipeline_loop() — frame capture failed.")
                state = FrameState(capture_ok=False)
                with self._lock:
                    self._frame_state = state
                continue

            frame_height, frame_width = frame.shape[:2]

            # ── 2. Detect ───────────────────────────────────────────────
            raw_detections: list[FaceDetection] = self._detector.detect(frame)

            # ── 3. Confidence gate + grace period ───────────────────────
            valid: Optional[FaceDetection] = None
            for det in raw_detections:
                if det.confidence >= STREAM_CONFIDENCE_THRESHOLD:
                    valid = det
                    break

            if valid is not None:
                # Fresh high-confidence detection — reset grace counter
                last_face = valid
                grace_counter = 0
            else:
                if last_face is not None and grace_counter < DETECTION_GRACE_FRAMES:
                    # Within grace period — hold the previous detection
                    valid = last_face
                    grace_counter += 1
                else:
                    # Grace period exhausted — clear tracked face
                    last_face = None
                    initialized = False
                    grace_counter = 0

            # ── 4a. EMA bbox smoothing ───────────────────────────────────
            face_for_state: Optional[FaceDetection] = None
            distance_cm: float = 0.0
            angle_deg: float = 0.0

            if valid is not None:
                rx = float(valid.bbox_x)
                ry = float(valid.bbox_y)
                rw = float(valid.bbox_width)
                rh = float(valid.bbox_height)

                if not initialized:
                    smooth_x, smooth_y, smooth_w, smooth_h = rx, ry, rw, rh
                    initialized = True
                else:
                    a = BBOX_SMOOTHING_ALPHA
                    smooth_x = a * rx + (1.0 - a) * smooth_x
                    smooth_y = a * ry + (1.0 - a) * smooth_y
                    smooth_w = a * rw + (1.0 - a) * smooth_w
                    smooth_h = a * rh + (1.0 - a) * smooth_h

                # Build a synthetic FaceDetection from the smoothed coords
                # for drawing and estimation; native int required by estimators.
                sx = int(round(smooth_x))
                sy = int(round(smooth_y))
                sw = max(1, int(round(smooth_w)))
                sh = max(1, int(round(smooth_h)))

                smoothed_face = FaceDetection(
                    bbox_x=sx,
                    bbox_y=sy,
                    bbox_width=sw,
                    bbox_height=sh,
                    center_x=sx + sw // 2,
                    center_y=sy + sh // 2,
                    confidence=valid.confidence,
                )

                # ── 4b. Estimate ─────────────────────────────────────────
                try:
                    distance_cm = self._distance_estimator.estimate(smoothed_face)
                    angle_deg = self._angle_estimator.estimate(
                        smoothed_face, frame_width
                    )
                except Exception as exc:
                    logger.debug("_pipeline_loop() — estimator error: %s", exc)

                face_for_state = smoothed_face

                # ── 4c. Draw overlay ──────────────────────────────────────
                cv2.rectangle(
                    frame,
                    (sx, sy),
                    (sx + sw, sy + sh),
                    BOUNDING_BOX_COLOR,
                    BOUNDING_BOX_THICKNESS,
                )

                conf_pct = round(valid.confidence * 100)
                label = (
                    f"Person {conf_pct}%  "
                    f"{distance_cm:.1f} cm  "
                    f"{angle_deg:+.1f}\u00b0"
                )
                label_y = max(sy - 10, 20)
                font = cv2.FONT_HERSHEY_SIMPLEX

                # Shadow pass for readability
                cv2.putText(
                    frame, label, (sx, label_y),
                    font, TEXT_SIZE, (0, 0, 0),
                    BOUNDING_BOX_THICKNESS + 2, cv2.LINE_AA,
                )
                # Foreground text
                cv2.putText(
                    frame, label, (sx, label_y),
                    font, TEXT_SIZE, COLOR_TEXT,
                    BOUNDING_BOX_THICKNESS, cv2.LINE_AA,
                )

            # ── 5. JPEG encode ───────────────────────────────────────────
            encode_ok, buffer = cv2.imencode(
                ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85]
            )
            jpeg: Optional[bytes] = buffer.tobytes() if encode_ok else None

            # ── 6. Write shared state (lock held only briefly) ───────────
            new_state = FrameState(
                capture_ok=True,
                face=face_for_state,
                smooth_x=smooth_x,
                smooth_y=smooth_y,
                smooth_w=smooth_w,
                smooth_h=smooth_h,
                distance_cm=distance_cm,
                angle_deg=angle_deg,
                grace_counter=grace_counter,
                frame_width=frame_width,
            )
            with self._lock:
                self._frame_state = new_state
                self._jpeg_bytes = jpeg

    # ------------------------------------------------------------------
    # Public API — endpoint methods (pure readers)
    # ------------------------------------------------------------------

    def process_frame(self) -> dict[str, Any]:
        """Return the latest pipeline result as a structured dictionary.

        This method does **not** read from the camera or run detection.
        It copies the current ``_frame_state`` snapshot under the lock and
        converts it to the API response format.

        Returns
        -------
        dict[str, Any]
            One of three shapes:

            **Capture failure**::

                {"success": False, "error": "Failed to capture frame."}

            **No face**::

                {"success": True, "face_detected": False}

            **Face detected**::

                {
                    "success": True,
                    "face_detected": True,
                    "distance_cm": float,
                    "angle_deg": float,
                    "bbox": {"x": int, "y": int, "width": int, "height": int},
                    "detection_confidence": float
                }
        """
        with self._lock:
            state = self._frame_state

        if not state.capture_ok:
            return {"success": False, "error": "Failed to capture frame."}

        if state.face is None:
            return {"success": True, "face_detected": False}

        face = state.face
        return {
            "success": True,
            "face_detected": True,
            "distance_cm": float(state.distance_cm),
            "angle_deg": float(state.angle_deg),
            "bbox": {
                "x": int(face.bbox_x),
                "y": int(face.bbox_y),
                "width": int(face.bbox_width),
                "height": int(face.bbox_height),
            },
            "detection_confidence": float(face.confidence),
        }

    def read_annotated_frame(self) -> Optional[bytes]:
        """Return the latest annotated JPEG frame bytes for MJPEG streaming.

        This method does **not** read from the camera, run detection, or
        perform any encoding work.  It simply returns a reference to the
        bytes object most recently written by the pipeline thread.

        Returns
        -------
        bytes or None
            JPEG bytes of the latest annotated frame, or ``None`` if the
            pipeline has not yet produced a frame.
        """
        with self._lock:
            return self._jpeg_bytes

    def calibrate(self, known_distance_cm: float) -> float:
        """Calibrate the focal length using the latest pipeline detection.

        Reads the current ``_frame_state`` snapshot.  If a face is present,
        uses its smoothed bounding box to compute a calibrated focal length.

        Parameters
        ----------
        known_distance_cm : float
            Physical distance in centimetres at calibration time.

        Returns
        -------
        float
            The newly calibrated focal length in pixels.

        Raises
        ------
        RuntimeError
            If no face is currently detected in the pipeline.
        ValueError
            If *known_distance_cm* is not positive.
        """
        with self._lock:
            state = self._frame_state

        if not state.capture_ok:
            raise RuntimeError(
                "Calibration failed: could not capture a frame from the camera."
            )

        if state.face is None:
            raise RuntimeError(
                "Calibration failed: no face was detected in the captured frame. "
                "Ensure the subject is visible and well-lit, then retry."
            )

        focal_length = self._calibrator.calculate_focal_length(
            face=state.face,
            known_distance_cm=known_distance_cm,
        )
        logger.info(
            "calibrate() — completed, known_distance=%.2f cm, "
            "focal_length=%.4f px.",
            known_distance_cm,
            focal_length,
        )
        return focal_length

    def shutdown(self) -> None:
        """Stop the pipeline thread and release all hardware resources.

        Safe to call multiple times; subsequent calls are no-ops.
        """
        if self._is_shutdown:
            logger.debug("shutdown() — already shut down; skipping.")
            return

        self._stop_event.set()
        self._pipeline_thread.join(timeout=3.0)

        self._camera.stop()
        self._detector.close()
        self._is_shutdown = True

        logger.info("FaceDistanceAPI shutdown completed — all resources released.")
