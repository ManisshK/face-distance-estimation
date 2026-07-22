"""
detector.py — Face detection engine for the Face Distance Estimation backend.

This module defines two public symbols:

* ``FaceDetection``  — a frozen dataclass representing a single detected face
  with pixel-space bounding box, centre coordinates, and detection confidence.
  All numeric fields are native Python ``int`` / ``float`` — never NumPy
  scalar types.

* ``FaceDetector``   — a class that wraps the OpenCV YuNet face detector
  (``cv2.FaceDetectorYN``), accepts raw BGR frames from OpenCV, and returns
  a list of ``FaceDetection`` objects.

Responsibilities
----------------
* Load the YuNet ONNX model from the path configured in ``config.py``.
* Validate incoming frames before passing them to the model.
* Run ``cv2.FaceDetectorYN`` inference on each frame.
* Convert raw OpenCV detection arrays into ``FaceDetection`` dataclass
  objects, ensuring all scalar values are native Python types.
* Cap results to ``MAX_FACES`` as configured.

Out of scope
------------
This module does **not** calculate distance, angle, calibration values,
confidence scores, or perform any visualisation or OpenCV drawing.

Logging is intentionally **not** configured here.  The application entry
point (``main.py``) is responsible for calling ``logging.basicConfig()``.

YuNet detection row layout
--------------------------
Each row in the ``faces`` matrix returned by ``cv2.FaceDetectorYN.detect``
has 15 columns::

    [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt,
     x_rcm, y_rcm, x_lcm, y_lcm, score]

Only the first four (bounding box) and the last (score) are used here.

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
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from numpy.typing import NDArray

from app.config import (
    MAX_FACES,
    MIN_DETECTION_CONFIDENCE,
    YUNET_MODEL_PATH,
    YUNET_NMS_THRESHOLD,
    YUNET_TOP_K,
)

# ---------------------------------------------------------------------------
# Module logger — configuration delegated to the application entry point
# ---------------------------------------------------------------------------

logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# YuNet output column indices (from OpenCV documentation)
# ---------------------------------------------------------------------------

_COL_X: int = 0
_COL_Y: int = 1
_COL_W: int = 2
_COL_H: int = 3
_COL_SCORE: int = 14


# ---------------------------------------------------------------------------
# FaceDetection dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FaceDetection:
    """Represents a single face detected in a video frame.

    All spatial fields are expressed in pixel coordinates.  Every field
    holds a **native Python scalar** (``int`` or ``float``) — NumPy scalar
    types are explicitly converted before storage so that callers never
    receive ``numpy.int64`` or ``numpy.float32`` values.

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
        Detection confidence score in ``[0.0, 1.0]`` as reported by YuNet.
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
    """Wraps OpenCV YuNet face detection and returns ``FaceDetection`` objects.

    All detection parameters are sourced from ``app.config``; nothing is
    hardcoded inside this class.  The detector supports both explicit
    lifecycle management and the context-manager protocol.

    The YuNet model is loaded from ``YUNET_MODEL_PATH`` (relative to the
    repository root), using ``MIN_DETECTION_CONFIDENCE``, ``YUNET_NMS_THRESHOLD``,
    and ``YUNET_TOP_K`` from ``app.config``.

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
        """Initialise and load the YuNet face detection model.

        Resolves ``YUNET_MODEL_PATH`` relative to the repository root
        (three levels above this file's directory), constructs a
        ``cv2.FaceDetectorYN`` instance, and logs successful initialisation.

        The initial input size is set to ``(1, 1)`` as a placeholder; it is
        updated to match the actual frame dimensions on every call to
        :meth:`detect`.

        Raises
        ------
        RuntimeError
            If the model file does not exist at the resolved path, or if
            OpenCV raises any error while loading the ONNX model.
        """
        self._detector: Optional[cv2.FaceDetectorYN] = None

        model_path: Path = self._resolve_model_path(YUNET_MODEL_PATH)

        logger.debug(
            "FaceDetector loading YuNet model from '%s'.",
            model_path,
        )

        if not model_path.is_file():
            raise RuntimeError(
                f"YuNet model file not found at '{model_path}'. "
                "Download 'face_detection_yunet_2023mar.onnx' and place it "
                f"at the configured YUNET_MODEL_PATH ('{YUNET_MODEL_PATH}')."
            )

        try:
            self._detector = cv2.FaceDetectorYN.create(
                str(model_path),
                "",                        # config file — not used by YuNet
                (1, 1),                    # placeholder; updated per frame
                score_threshold=MIN_DETECTION_CONFIDENCE,
                nms_threshold=YUNET_NMS_THRESHOLD,
                top_k=YUNET_TOP_K,
            )
        except cv2.error as exc:
            raise RuntimeError(
                f"OpenCV failed to load YuNet model from '{model_path}': {exc}"
            ) from exc

        logger.debug(
            "FaceDetector initialised — model='%s', "
            "score_threshold=%.2f, nms_threshold=%.2f, top_k=%d, max_faces=%d.",
            model_path.name,
            MIN_DETECTION_CONFIDENCE,
            YUNET_NMS_THRESHOLD,
            YUNET_TOP_K,
            MAX_FACES,
        )

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
        """Release resources when exiting a ``with`` block.

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

        Updates the YuNet input size to match the actual frame dimensions,
        runs inference, and converts the raw detection array into a list of
        ``FaceDetection`` objects.

        Parameters
        ----------
        frame : NDArray[np.uint8]
            An OpenCV BGR image as a ``uint8`` NumPy array of shape
            ``(height, width, 3)``.  Must not be ``None`` or empty.

        Returns
        -------
        list[FaceDetection]
            A (possibly empty) list of ``FaceDetection`` objects, one per
            detected face, capped at ``MAX_FACES``.  Never returns ``None``.

        Notes
        -----
        * If the frame is ``None``, empty, or has an unexpected shape, an
          empty list is returned and a WARNING is logged.
        * If OpenCV raises any exception during inference, an empty list is
          returned and the error is logged at ERROR level.
        * All numeric values in the returned objects are native Python types.
        """
        if not self._is_frame_valid(frame):
            return []

        if self._detector is None:
            logger.error(
                "detect() called on a closed FaceDetector. "
                "Re-initialise or use a new instance."
            )
            return []

        frame_height: int = frame.shape[0]
        frame_width: int = frame.shape[1]

        try:
            self._detector.setInputSize((frame_width, frame_height))
            _, raw_faces = self._detector.detect(frame)
        except cv2.error as exc:
            logger.error(
                "OpenCV YuNet inference failed on %dx%d frame: %s",
                frame_width,
                frame_height,
                exc,
                exc_info=True,
            )
            return []

        if raw_faces is None:
            logger.debug("No faces detected in %dx%d frame.", frame_width, frame_height)
            return []

        detections: list[FaceDetection] = self._convert_detections(raw_faces)

        logger.debug(
            "Detection succeeded — %d face(s) found in %dx%d frame.",
            len(detections),
            frame_width,
            frame_height,
        )

        return detections

    def close(self) -> None:
        """Release the YuNet detector and free associated resources.

        Safe to call multiple times — subsequent calls after the first are
        no-ops.  After this method returns, :meth:`detect` will return an
        empty list.
        """
        if self._detector is not None:
            # cv2.FaceDetectorYN does not expose an explicit close/release
            # method; dereferencing the object allows the garbage collector
            # to reclaim its memory.
            self._detector = None
            logger.debug("FaceDetector closed — YuNet resources released.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_model_path(relative_path: str) -> Path:
        """Resolve *relative_path* against the repository root.

        The repository root is calculated as three directory levels above
        this source file:
        ``<repo_root>/backend/app/detector.py``  →  ``<repo_root>``.

        Parameters
        ----------
        relative_path : str
            Path to the model file relative to the repository root, as
            configured in ``YUNET_MODEL_PATH``.

        Returns
        -------
        Path
            Absolute path to the model file.
        """
        repo_root: Path = Path(__file__).resolve().parent.parent.parent
        return repo_root / relative_path

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
            ``True`` if *frame* can safely be passed to the YuNet detector.
        """
        if frame is None:
            logger.warning("detect() received a None frame; skipping.")
            return False

        if not isinstance(frame, np.ndarray):
            logger.warning(
                "detect() received an unexpected type %s; expected numpy.ndarray.",
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
        raw_faces: NDArray[np.float32],
    ) -> list[FaceDetection]:
        """Convert the raw YuNet output array into ``FaceDetection`` objects.

        Applies the ``MAX_FACES`` cap so the returned list never exceeds the
        configured limit.  All NumPy scalar values are explicitly cast to
        native Python ``int`` or ``float`` to ensure no ``numpy.int64`` or
        ``numpy.float32`` values leak into the public API.

        YuNet row layout (15 columns)::

            [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt,
             x_rcm, y_rcm, x_lcm, y_lcm, score]

        Parameters
        ----------
        raw_faces : NDArray[np.float32]
            The faces matrix returned by ``cv2.FaceDetectorYN.detect``.
            Shape is ``(N, 15)`` where N ≥ 1.

        Returns
        -------
        list[FaceDetection]
            Converted detections, capped at ``MAX_FACES``.
        """
        detections: list[FaceDetection] = []

        for row in raw_faces[:MAX_FACES]:
            bbox_x: int = int(row[_COL_X])
            bbox_y: int = int(row[_COL_Y])
            bbox_width: int = int(row[_COL_W])
            bbox_height: int = int(row[_COL_H])
            confidence: float = float(row[_COL_SCORE])

            center_x: int = bbox_x + bbox_width // 2
            center_y: int = bbox_y + bbox_height // 2

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
