"""
main.py — FastAPI application entry point for the Face Distance Estimation backend.

This module is responsible for:

* Configuring the root logging system (the only module in the project that
  calls ``logging.basicConfig()``).
* Creating the FastAPI application instance.
* Managing the ``FaceDistanceAPI`` lifecycle via a lifespan context manager.
* Defining all HTTP endpoints.

Responsibilities
----------------
* Logging configuration.
* FastAPI app creation and lifespan management.
* HTTP route definitions and request/response handling.
* Delegating all business logic to :class:`~app.api.FaceDistanceAPI`.

Out of scope
------------
This module does **not** implement face detection, distance estimation, angle
estimation, calibration logic, or confidence scoring.  All business logic
lives in ``api.py`` and its dependencies.

Running the server
------------------
::

    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Iterator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api import FaceDistanceAPI
from app.config import APP_NAME, APP_VERSION, LOG_FORMAT, LOG_LEVEL

# ---------------------------------------------------------------------------
# Logging — configured ONCE here; all other modules use getLogger(__name__)
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format=LOG_FORMAT,
)

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class CalibrateRequest(BaseModel):
    """Request body for the ``POST /calibrate`` endpoint.

    Attributes
    ----------
    known_distance_cm : float
        The measured physical distance in centimetres between the camera lens
        and the subject's face at the moment of calibration capture.
        Must be strictly positive.
    """

    known_distance_cm: float = Field(
        ...,
        gt=0,
        description=(
            "Known physical distance in centimetres at which the subject "
            "is positioned during calibration.  Must be strictly positive."
        ),
        examples=[100.0],
    )


class CalibrateResponse(BaseModel):
    """Response body for the ``POST /calibrate`` endpoint.

    Attributes
    ----------
    focal_length : float
        The calibrated focal length in pixels derived from the capture.
    """

    focal_length: float = Field(
        ...,
        description="Calibrated focal length in pixels.",
    )


# ---------------------------------------------------------------------------
# Lifespan — startup and shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage the ``FaceDistanceAPI`` lifecycle for the FastAPI application.

    On startup a single :class:`~app.api.FaceDistanceAPI` instance is created
    and stored in ``app.state.api``.  On shutdown ``api.shutdown()`` is called
    to release the webcam and MediaPipe resources.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance whose ``state`` is used to store
        the shared :class:`~app.api.FaceDistanceAPI` object.

    Yields
    ------
    None
        Control is yielded to FastAPI while the application is running.

    Raises
    ------
    RuntimeError
        If :class:`~app.api.FaceDistanceAPI` cannot be initialised (e.g.
        camera unavailable).  The error is logged before propagating.
    """
    logger.info("Application startup — initialising FaceDistanceAPI.")

    try:
        app.state.api = FaceDistanceAPI()
    except RuntimeError as exc:
        logger.critical(
            "Failed to initialise FaceDistanceAPI during startup: %s",
            exc,
            exc_info=True,
        )
        raise

    logger.info("Application startup complete.")

    yield  # — application is running —

    logger.info("Application shutdown — releasing resources.")
    app.state.api.shutdown()
    logger.info("Application shutdown complete.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app: FastAPI = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get(
    "/",
    summary="Application info",
    response_description="Application name, version, and running status.",
)
def root() -> dict[str, str]:
    """Return basic application metadata and a running status indicator.

    Returns
    -------
    dict[str, str]
        A dictionary with ``application``, ``version``, and ``status`` keys.

    Example response::

        {
            "application": "Face Distance Estimation",
            "version": "1.0.0",
            "status": "running"
        }
    """
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }


@app.get(
    "/health",
    summary="Health check",
    response_description="Service health status.",
)
def health() -> dict[str, str]:
    """Return a minimal health-check response.

    Intended for use by load balancers, container orchestration probes, and
    monitoring systems to verify that the service is up and responding.

    Returns
    -------
    dict[str, str]
        A dictionary with a single ``status`` key set to ``"healthy"``.

    Example response::

        {"status": "healthy"}
    """
    return {"status": "healthy"}


@app.get(
    "/frame",
    summary="Process one video frame",
    response_description=(
        "Detection result: capture failure, no face detected, or full "
        "distance/angle measurements."
    ),
)
def frame() -> dict[str, Any]:
    """Capture one frame and return the full detection-estimation result.

    Delegates entirely to :meth:`~app.api.FaceDistanceAPI.process_frame`.
    The returned dictionary is passed through unmodified.

    Returns
    -------
    dict[str, Any]
        One of three shapes, as produced by
        :meth:`~app.api.FaceDistanceAPI.process_frame`:

        **Capture failure**::

            {"success": False, "error": "Failed to capture frame."}

        **No face detected**::

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

    Raises
    ------
    HTTPException
        HTTP 500 if an unexpected internal error occurs during frame
        processing.
    """
    try:
        return app.state.api.process_frame()
    except Exception as exc:
        logger.error(
            "Unexpected error in GET /frame: %s",
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the frame.",
        ) from exc


@app.post(
    "/calibrate",
    summary="Calibrate focal length",
    response_model=CalibrateResponse,
    response_description="The calibrated focal length in pixels.",
)
def calibrate(request: CalibrateRequest) -> CalibrateResponse:
    """Calibrate the camera focal length at a known distance.

    Captures one frame, detects the first visible face, and derives the
    focal length using the pinhole camera model.  The calibrated value is
    stored in the backend for future distance estimates.

    Parameters
    ----------
    request : CalibrateRequest
        JSON body containing ``known_distance_cm`` — the precise physical
        distance in centimetres between the camera and the subject's face.

    Returns
    -------
    CalibrateResponse
        A response body containing the newly calibrated ``focal_length``
        in pixels.

    Raises
    ------
    HTTPException
        HTTP 400 if calibration cannot be completed because no face was
        detected, the frame could not be captured, or the supplied distance
        is invalid.

        HTTP 500 if an unexpected internal error occurs.
    """
    try:
        focal_length: float = app.state.api.calibrate(
            known_distance_cm=request.known_distance_cm,
        )
        return CalibrateResponse(focal_length=focal_length)

    except (RuntimeError, ValueError) as exc:
        logger.warning(
            "Calibration request failed (400): %s",
            exc,
        )
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.error(
            "Unexpected error in POST /calibrate: %s",
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during calibration.",
        ) from exc


# ---------------------------------------------------------------------------
# MJPEG stream helpers
# ---------------------------------------------------------------------------

# Target inter-frame delay in seconds.  30 fps ≈ 33 ms between frames.
_STREAM_FRAME_INTERVAL: float = 1.0 / 30.0

# MJPEG multipart boundary token.
_MJPEG_BOUNDARY: bytes = b"--frameboundary"

# Content-type header for MJPEG streams.
_MJPEG_CONTENT_TYPE: str = (
    "multipart/x-mixed-replace; boundary=frameboundary"
)


async def _mjpeg_generator(api: FaceDistanceAPI) -> AsyncGenerator[bytes, None]:
    """Async generator that yields MJPEG multipart frames indefinitely.

    Each iteration:
    1. Calls ``api.read_annotated_frame()`` to get a JPEG-encoded, annotated
       frame from the shared camera/detector.
    2. Wraps the bytes in the MJPEG multipart envelope.
    3. Yields the envelope bytes to the StreamingResponse.
    4. Sleeps for the configured inter-frame interval so the loop targets
       ~30 fps without busy-spinning.

    The generator exits cleanly when the client disconnects — FastAPI /
    Starlette propagates a ``GeneratorExit`` or ``asyncio.CancelledError``
    which terminates the async for-loop in the route.

    Parameters
    ----------
    api : FaceDistanceAPI
        The shared application API instance that owns the camera and detector.

    Yields
    ------
    bytes
        One MJPEG multipart envelope per camera frame.
    """
    while True:
        # Offload the synchronous OpenCV work to a thread so the event loop
        # is not blocked during frame capture and encoding.
        frame_bytes: bytes | None = await asyncio.get_event_loop().run_in_executor(
            None, api.read_annotated_frame
        )

        if frame_bytes is not None:
            # Build the MJPEG multipart envelope.
            envelope = (
                _MJPEG_BOUNDARY + b"\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n"
                b"\r\n" +
                frame_bytes +
                b"\r\n"
            )
            yield envelope

        # Yield control back to the event loop between frames.
        await asyncio.sleep(_STREAM_FRAME_INTERVAL)


@app.get(
    "/video",
    summary="Live MJPEG video stream with bounding-box overlay",
    response_description="Continuous MJPEG stream of annotated camera frames.",
)
async def video() -> StreamingResponse:
    """Stream live annotated camera frames as an MJPEG multipart response.

    Each frame is captured from the shared ``Camera`` instance, passed
    through the shared ``FaceDetector``, annotated with a bounding box and
    label (confidence, distance, angle), JPEG-encoded, and yielded as a
    multipart envelope.

    The stream continues until the client disconnects.  No new camera or
    detector instances are created — the stream reuses the objects already
    owned by ``FaceDistanceAPI``.

    Returns
    -------
    StreamingResponse
        An MJPEG ``multipart/x-mixed-replace`` streaming response.
        Consume it with ``<img src="/video" />`` in the browser.

    Notes
    -----
    * The ``GET /frame`` endpoint continues to work independently.
      Both endpoints share the same camera but operate on separate
      ``read()`` calls, so neither blocks the other.
    * Target frame rate is 30 fps; actual rate depends on camera speed
      and detection latency.
    """
    return StreamingResponse(
        _mjpeg_generator(app.state.api),
        media_type=_MJPEG_CONTENT_TYPE,
    )
