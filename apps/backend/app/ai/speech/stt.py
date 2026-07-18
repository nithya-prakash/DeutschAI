"""Speech-to-text wrapper for Conversation Mode.

Uses `faster-whisper` (CTranslate2-based, no torch) rather than the OpenAI
Whisper API — runs fully locally on CPU: no API key, no per-request cost,
works offline once the model is cached. Same local-model philosophy as
`app/ai/rag/embedder.py`'s fastembed choice.
"""
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from faster_whisper import WhisperModel

from app.core.config import get_settings

settings = get_settings()

_CACHE_DIR = Path(__file__).resolve().parents[3] / ".whisper_cache"


class Transcriber(Protocol):
    """What `transcribe_audio` needs from a Whisper model — narrow enough
    that tests can pass a fake without loading real weights."""

    def transcribe(self, audio_path: str, language: str) -> tuple[object, object]: ...


@lru_cache
def get_whisper_model() -> WhisperModel:
    _CACHE_DIR.mkdir(exist_ok=True)
    return WhisperModel(
        settings.WHISPER_MODEL_SIZE,
        device="cpu",
        compute_type="int8",
        download_root=str(_CACHE_DIR),
    )


def transcribe(model: Transcriber, audio_bytes: bytes, suffix: str = ".webm") -> str:
    """Transcribe raw audio bytes (whatever format the browser recorded —
    faster-whisper decodes via bundled ffmpeg/av) to German text. Takes the
    model as a parameter, mirroring `tutor_agent.build_tutor_graph`'s
    DI-for-testability shape."""
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, _info = model.transcribe(tmp.name, language="de")
        return "".join(segment.text for segment in segments).strip()


def transcribe_audio(audio_bytes: bytes, suffix: str = ".webm") -> str:
    """Transcribe against the real, locally-cached Whisper model."""
    return transcribe(get_whisper_model(), audio_bytes, suffix=suffix)


def is_model_cached() -> bool:
    """Whether the Whisper model has already been downloaded — used by the
    admin panel's system-health view, doesn't trigger a download itself."""
    return _CACHE_DIR.is_dir() and any(_CACHE_DIR.iterdir())
