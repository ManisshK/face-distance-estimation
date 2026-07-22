"""
detector.py — Face detection engine for the Face Distance Estimation backend.

This module defines two public symbols:

* ``FaceDetection``  — a dataclass representing a single detected face with
  pixel-space bounding box, centre coordinates, and detection confidence.
* ``FaceDetector``   — a class that wraps MediaPipe Face Detection, accepts
  raw BGR frames from OpenCV, and returns a list of ``FaceDetection`` objects.

Responsibilities
----------------
* Convert BGR frames to RGB for MediaPipe.
* Run MediaPipe Face Detection with parameters sourced from ``config.py``.
* Convert normalised MediaPipe bounding boxes to pixel coordinates.
* Return structured ``FaceDetection`` objects to callers.

Out of scope
------------
This module does **not** calculate distance, angle, calibration values,
confidence scores, or perform any visualisation or OpenCV drawing.

Logging is intentionally **not** configured here.  The application entry
point (``main.py``) is responsible for calling ``logging.basicConfig()``.

Usage
-----
::

    from app.detector import FaceDetector, FaceDetection

    # Explicit lifecycle
    detector = FaceDetector()
    detections: list[FaceDetection] = detector.detect(frame)
    detector.close()

    # Context-manager lifecycle
    with FaceDetector() as detector:
        detections = detector.detect(frame)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from numpy.typing import NDArray

from app.config import MAX_FACES, MIN_DETECTION_CONFIDENCE

# ---------------------------------------------------------------------------
# Module logger — configuration delegated to the application entry point
# ---------------------------------------------------------------------------

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FaceDetection dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FaceDetection:
    """Represents a single face detected in a video frame.

    All spatial fields are expressed in pixel coordinates derived from the
    actual frame dimensions.  The ``confidence`` field is the raw score
    returned by MediaPipe in the range ``[0.0, 1.0]``.

    Attributes
    ----------
    bbox_x : int
        X coordinate (in pixels) of the top-left corner of the bounding box.
    bbox_y : int
        Y coordinate (in pixels) of the top-left corner of the bounding box.
    bbox_width : int
        Width of the bounding box in pixels.
    bbox_height : int
        Height of the bounding box in pixels.
    center_x : int
        X coordinate (in pixels) of the bounding-box centre.
    center_y : int
        Y coordinate (in pixels) of the bounding-box centre.
    confidence : float
        Detection confidence score in ``[0.0, 1.0]`` as reported by
        MediaPipe Face Detection.
    """

    bbox_x: int
    bbox_y: int
    bbox_width: int
    bbox_height: int
    center_x: int
    center_y: int
    confidence: float


# ---------------------------------------------------------------------------
# FaceDetector class
# ---------------------------------------------------------------------------


class FaceDetector:
    """Wraps MediaPipe Face Detection and converts results to ``FaceDetection`` objects.

    All detection parameters are sourced from ``app.config``; nothing is
    hardcoded inside this class.  The detector supports both explicit
    lifecycle management and the context-manager protocol.

    Typical usage — explicit
    ------------------------
    ::

        detector = FaceDetector()
        detections = detector.detect(frame)
        detector.close()

    Typical usage — context manager
    --------------------------------
    ::

        with FaceDetector() as detector:
            detections = detector.detect(frame)
    """

    def __init__(self) -> None:
        """Initialise MediaPipe Face Detection with parameters from ``config.py``.

        Creates and starts the MediaPipe ``FaceDetection`` solution using
        ``MIN_DETECTION_CONFIDENCE`` and ``MAX_FACES`` imported from
        ``config.py``.  No frame is processed here.

        Raises
        ------
        RuntimeError
            If MediaPipe cannot be initialised (e.g. missing model files).
        """
        self._face_detection: Optional[mp.solutions.face_detection.FaceDetection] = None

        try:
            self._face_detection = mp.solutions.face_detection.FaceDetection(
                min_detection_confidence=MIN_DETECTION_CONFIDENCE,
                model_selection=0,  # 0 = short-range model (≤ 2 m); 1 = full-range
            )
            logger.info(
                "FaceDetector initialised — min_confidence=%.2f, max_faces=%d",
                MIN_DETECTION_CONFIDENCE,
                MAX_FACES,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialise MediaPipe FaceDetection: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------

    def __enter__(self) -> "FaceDetector":
        """Return this instance for use inside a ``with`` block.

        The detector is already initialised by ``__init__``, so no additional
        setup is performed here.

        Returns
        -------
        FaceDetector
            This ``FaceDetector`` instance, ready to use.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Release MediaPipe resources when exiting a ``with`` block.

        Calls :meth:`close` unconditionally, ensuring resources are freed
        whether the block exited normally or via an exception.

        Parameters
        ----------
        exc_type:
            The exception class, if any was raised inside the block.
        exc_val:
            The exception instance, if any was raised inside the block.
        exc_tb:
            The traceback, if any was raised inside the block.
        """
        self.close()

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def detect(self, frame: NDArray[np.uint8]) -> list[FaceDetection]:
        """Detect faces in a single BGR video frame.

        Converts the frame from BGR to RGB, passes it to MediaPipe Face
        Detection, and converts the normalised bounding boxes returned by
        MediaPipe into pixel-space ``FaceDetection`` objects.

        Parameters
        ----------
        frame : NDArray[np.uint8]
            An OpenCV BGR image as a ``uint8`` NumPy array of shape
            ``(height, width, 3)``.  Must not be ``None`` or empty.

        Returns
        -------
        list[FaceDetection]
            A (possibly empty) list of ``FaceDetection`` objects, one per
            detected face.  The list is capped at ``MAX_FACES`` results from
            ``config.py``.  Never returns ``None``.

        Notes
        -----
        * If ``frame`` is ``None``, empty, or has an unexpected shape, an
          empty list is returned and the error is logged.
        * If MediaPipe raises an exception, an empty list is returned and
          the exception is logged at ERROR level.
        """
        if not self._is_frame_valid(frame):
            return []

        if self._face_detection is None:
            logger.error(
                "detect() called on a closed FaceDetector. "
                "Re-initialise or use a new instance."
            )
            return []

        try:
            rgb_frame: NDArray[np.uint8] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False

            results = self._face_detection.process(rgb_frame)

            if not results.detections:
                logger.debug("No faces detected in frame.")
                return []

            frame_height, frame_width = frame.shape[:2]
            detections = self._convert_detections(
                results.detections, frame_width, frame_height
            )

            logger.debug(
                "Detection succeeded — %d face(s) found in %dx%d frame.",
                len(detections),
                frame_width,
                frame_height,
            )
            return detections

        except Exception as exc:
            logger.error(
                "MediaPipe detection failed: %s",
                exc,
                exc_info=True,
            )
            return []

    def close(self) -> None:
        """Release MediaPipe resources held by this detector.

        Safe to call multiple times — subsequent calls after the first are
        no-ops.  After this method returns, :meth:`detect` will return an
        empty list.
        """
        if self._face_detection is not None:
            self._face_detection.close()
            self._face_detection = None
            logger.info("FaceDetector closed — MediaPipe resources released.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_frame_valid(frame: object) -> bool:
        """Return ``True`` when *frame* is a non-empty, 3-channel NumPy array.

        Parameters
        ----------
        frame : object
            The value to validate.

        Returns
        -------
        bool
            ``True`` if *frame* can safely be passed to MediaPipe.
        """
        if frame is None:
            logger.warning("detect() received a None frame; skipping.")
            return False

        if not isinstance(frame, np.ndarray):
            logger.warning(
                "detect() received an unexpected type %s; skipping.",
                type(frame).__name__,
            )
            return False

        if frame.size == 0:
            logger.warning("detect() received an empty frame; skipping.")
            return False

        if frame.ndim != 3 or frame.shape[2] != 3:
            logger.warning(
                "detect() received a frame with unexpected shape %s; "
                "expected (H, W, 3).",
                frame.shape,
            )
            return False

        return True

    @staticmethod
    def _convert_detections(
        raw_detections: list,
        frame_width: int,
        frame_height: int,
    ) -> list[FaceDetection]:
        """Convert MediaPipe detections to pixel-space ``FaceDetection`` objects.

        Applies the ``MAX_FACES`` cap imported from ``config.py`` so the
        returned list never exceeds the configured limit.

        Parameters
        ----------
        raw_detections : list
            The ``results.detections`` list returned by MediaPipe.
        frame_width : int
            Width of the source frame in pixels, used to de-normalise
            horizontal coordinates.
        frame_height : int
            Height of the source frame in pixels, used to de-normalise
            vertical coordinates.

        Returns
        -------
        list[FaceDetection]
            Converted detections, capped at ``MAX_FACES``.
        """
        detections: list[FaceDetection] = []

        for raw in raw_detections[:MAX_FACES]:
            bounding_box = raw.location_data.relative_bounding_box

            bbox_x = max(0, int(bounding_box.xmin * frame_width))
            bbox_y = max(0, int(bounding_box.ymin * frame_height))
            bbox_width = int(bounding_box.width * frame_width)
            bbox_height = int(bounding_box.height * frame_height)

            center_x = bbox_x + bbox_width // 2
            center_y = bbox_y + bbox_height // 2

            confidence = float(raw.score[0]) if raw.score else 0.0

            detections.append(
                FaceDetection(
                    bbox_x=bbox_x,
                    bbox_y=bbox_y,
                    bbox_width=bbox_width,
                    bbox_height=bbox_height,
                    center_x=center_x,
                    center_y=center_y,
                    confidence=confidence,
                )
            )

        return detections
