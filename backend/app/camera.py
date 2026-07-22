"""
camera.py — Webcam lifecycle management for the Face Distance Estimation backend.

This module defines a single public class, ``Camera``, whose sole responsibility
is opening, reading from, and releasing an OpenCV ``VideoCapture`` device.

It contains **no** face-detection logic, distance estimation, angle calculation,
calibration routines, confidence scoring, or FastAPI route definitions.  All
hardware parameters are imported from ``config.py``; no values are hardcoded.

Logging is intentionally **not** configured here.  Callers (e.g. ``main.py``)
are responsible for calling ``logging.basicConfig()`` or equivalent before use.

Usage
-----
::

    from app.camera import Camera

    # Explicit lifecycle
    cam = Camera()
    cam.start()
    success, frame = cam.read()
    cam.stop()

    # Context-manager lifecycle
    with Camera() as cam:
        success, frame = cam.read()
"""

from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np
from numpy.typing import NDArray

from app.config import (
    AUTO_EXPOSURE,
    CAMERA_INDEX,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    TARGET_FPS,
)

# ---------------------------------------------------------------------------
# Module logger — configuration delegated to the application entry point
# ---------------------------------------------------------------------------

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Camera class
# ---------------------------------------------------------------------------


class Camera:
    """Manages a single webcam device via OpenCV's ``VideoCapture`` API.

    This class follows the Single Responsibility Principle: it handles
    *only* webcam lifecycle management (open, read, close).  All camera
    configuration values are sourced from ``app.config``; nothing is
    hardcoded inside this class.

    The class supports both explicit lifecycle management and the context
    manager protocol for guaranteed resource cleanup.

    Typical usage — explicit
    ------------------------
    ::

        cam = Camera()
        cam.start()                     # opens hardware
        success, frame = cam.read()     # grabs a frame
        w, h = cam.get_resolution()
        fps  = cam.get_fps()
        cam.stop()                      # releases hardware

    Typical usage — context manager
    --------------------------------
    ::

        with Camera() as cam:
            success, frame = cam.read()
    """

    def __init__(self) -> None:
        """Prepare internal state only — does NOT open any camera device.

        Constructing a ``Camera`` instance is side-effect-free.  No hardware
        resource is acquired here.  Call :meth:`start` explicitly, or use the
        class as a context manager, when you are ready to open the webcam.
        """
        self._capture: Optional[cv2.VideoCapture] = None

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------

    def __enter__(self) -> "Camera":
        """Open the webcam and return this instance for use in a ``with`` block.

        Calls :meth:`start` so the camera is ready immediately upon entering
        the context.

        Returns
        -------
        Camera
            This ``Camera`` instance, already started.

        Raises
        ------
        RuntimeError
            If the camera cannot be opened (propagated from :meth:`start`).
        """
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Release the webcam when exiting a ``with`` block.

        Calls :meth:`stop` unconditionally, ensuring hardware is released
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
        self.stop()

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Open the webcam device and apply the configured capture properties.

        If the camera is already open this method returns immediately without
        creating a new ``VideoCapture`` object (idempotent).

        Creates a ``cv2.VideoCapture`` object using ``CAMERA_INDEX`` from
        ``config.py``, then applies ``FRAME_WIDTH``, ``FRAME_HEIGHT``,
        ``TARGET_FPS``, and ``AUTO_EXPOSURE``.  Logs the actual resolution
        and FPS reported by OpenCV after the device is open.

        Raises
        ------
        RuntimeError
            If the camera cannot be opened (e.g. device unavailable or index
            out of range).
        """
        if self.is_open():
            logger.debug("Camera already started.")
            return

        logger.info(
            "Camera starting — device index %d, requested %dx%d @ %d FPS",
            CAMERA_INDEX,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            TARGET_FPS,
        )

        capture = cv2.VideoCapture(CAMERA_INDEX)

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        capture.set(cv2.CAP_PROP_FPS, TARGET_FPS)
        capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, AUTO_EXPOSURE)

        if not capture.isOpened():
            capture.release()
            raise RuntimeError(
                f"Cannot open camera at device index {CAMERA_INDEX}. "
                "Ensure the webcam is connected and not in use by another application."
            )

        self._capture = capture

        actual_w = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self._capture.get(cv2.CAP_PROP_FPS)

        logger.info(
            "Camera opened successfully — device index %d, actual resolution %dx%d @ %.1f FPS",
            CAMERA_INDEX,
            actual_w,
            actual_h,
            actual_fps,
        )

    def read(self) -> tuple[bool, Optional[NDArray[np.uint8]]]:
        """Capture and return a single frame from the webcam.

        Returns
        -------
        tuple[bool, NDArray[np.uint8] | None]
            A ``(success, frame)`` pair that mirrors the OpenCV convention:

            * ``(True, frame)``  — frame captured successfully as a
              ``uint8`` NumPy array of shape ``(H, W, 3)`` in BGR order.
            * ``(False, None)``  — capture failed; the caller should decide
              whether to retry or abort.

        Raises
        ------
        RuntimeError
            If this method is called before :meth:`start` has been called.
        """
        if self._capture is None:
            raise RuntimeError(
                "Camera.read() called before Camera.start(). "
                "Call start() to open the webcam first."
            )

        try:
            success, frame = self._capture.read()
            if not success:
                logger.warning(
                    "Frame capture returned failure flag from device index %d.",
                    CAMERA_INDEX,
                )
                return False, None
            return True, frame
        except Exception as exc:  # pragma: no cover — hardware-level fault
            logger.error(
                "Unexpected error during frame capture on device index %d: %s",
                CAMERA_INDEX,
                exc,
                exc_info=True,
            )
            return False, None

    def is_open(self) -> bool:
        """Return ``True`` if the webcam is currently active.

        Delegates to ``cv2.VideoCapture.isOpened()`` so that the return value
        reflects the *actual* hardware state rather than a cached flag.

        Returns
        -------
        bool
            ``True`` only when the underlying ``VideoCapture`` exists *and*
            reports itself as open; ``False`` in all other cases (not started,
            already stopped, or device disconnected).
        """
        return self._capture is not None and self._capture.isOpened()

    def stop(self) -> None:
        """Release the webcam device and free all associated resources.

        Safe to call multiple times and safe to call even if :meth:`start`
        was never called — subsequent calls after the first are no-ops.
        After this method returns, :meth:`is_open` will return ``False``.
        """
        if self._capture is not None:
            if self._capture.isOpened():
                self._capture.release()
                logger.info(
                    "Camera closed — device index %d released.",
                    CAMERA_INDEX,
                )
            self._capture = None

    def get_resolution(self) -> tuple[int, int]:
        """Return the actual capture resolution currently reported by OpenCV.

        Queries ``cv2.CAP_PROP_FRAME_WIDTH`` and ``cv2.CAP_PROP_FRAME_HEIGHT``
        from the live ``VideoCapture`` object.  The returned values reflect
        what the hardware driver is *actually* delivering, which may differ
        from the requested ``FRAME_WIDTH``/``FRAME_HEIGHT`` in ``config.py``.

        Returns
        -------
        tuple[int, int]
            ``(width, height)`` in pixels as integers.  Either value may be
            ``0`` when the driver does not report the property.

        Raises
        ------
        RuntimeError
            If called when the camera is not open.  Call :meth:`start` first.
        """
        if not self.is_open():
            raise RuntimeError(
                "Camera.get_resolution() called while camera is not open. "
                "Call start() before querying resolution."
            )
        width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))   # type: ignore[union-attr]
        height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))  # type: ignore[union-attr]
        return width, height

    def get_fps(self) -> float:
        """Return the actual frames-per-second rate reported by OpenCV.

        Queries ``cv2.CAP_PROP_FPS`` from the live ``VideoCapture`` object.
        The returned value reflects what the hardware driver reports, which
        may differ from the requested ``TARGET_FPS`` in ``config.py``.
        A return value of ``0.0`` indicates the driver does not report FPS.

        Returns
        -------
        float
            Frames per second (e.g. ``30.0``).  May be ``0.0`` when the
            driver does not expose this property.

        Raises
        ------
        RuntimeError
            If called when the camera is not open.  Call :meth:`start` first.
        """
        if not self.is_open():
            raise RuntimeError(
                "Camera.get_fps() called while camera is not open. "
                "Call start() before querying FPS."
            )
        return self._capture.get(cv2.CAP_PROP_FPS)  # type: ignore[union-attr]
