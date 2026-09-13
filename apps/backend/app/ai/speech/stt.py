"""Speech-to-text wrapper for Conversation Mode.

Uses `faster-whisper` (CTranslate2-based, no torch) rather than the OpenAI
Whisper API — runs fully locally on CPU: no API key, no per-request cost,
works offline once the model is cached. Same local-model philosophy as
`app/ai/rag/embedder.py`'s fastembed choice.

Pronunciation and fluency scores are also derived here, from Whisper's own
decode signal (word-level confidence and timing) rather than from the
Conversation Agent, which only ever sees text and has no audio signal to
judge either from. Both are heuristic proxies, not a phonetic or certified
assessment — see `_pronunciation_score`/`_fluency_score` below.
"""
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Protocol

from faster_whisper import WhisperModel

from app.core.config import get_settings

settings = get_settings()

_CACHE_DIR = Path(__file__).resolve().parents[3] / ".whisper_cache"

# Natural conversational speaking-rate band (words per minute) — scores peak
# at 100 inside this range and decay outside it in either direction.
_FLUENT_WPM_LOW = 90
_FLUENT_WPM_HIGH = 160
# Inter-word gaps longer than this are treated as a disfluent pause.
_PAUSE_GAP_SECONDS = 0.6
_PAUSE_PENALTY_PER_GAP = 10
_MAX_PAUSE_PENALTY = 40


class Transcriber(Protocol):
    """What `transcribe_audio` needs from a Whisper model — narrow enough
    that tests can pass a fake without loading real weights."""

    def transcribe(
        self, audio_path: str, language: str, word_timestamps: bool
    ) -> tuple[object, object]: ...


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    pronunciation_score: int | None  # 0-100, None if no words were recognized
    fluency_score: int | None  # 0-100, None if fewer than 2 words (no rate signal)


@lru_cache
def get_whisper_model() -> WhisperModel:
    _CACHE_DIR.mkdir(exist_ok=True)
    return WhisperModel(
        settings.WHISPER_MODEL_SIZE,
        device="cpu",
        compute_type="int8",
        download_root=str(_CACHE_DIR),
    )


def _pronunciation_score(words: list) -> int | None:
    """Mean per-word decode confidence, scaled to 0-100. Decoder confidence
    correlates with clear, standard pronunciation, but also reacts to
    background noise and unusual words — a heuristic proxy, not a phonetic
    pronunciation assessment."""
    if not words:
        return None
    mean_probability = sum(word.probability for word in words) / len(words)
    return max(0, min(100, round(mean_probability * 100)))


def _fluency_score(words: list) -> int | None:
    """Speaking rate (words/minute) scored highest in a natural
    conversational band, decaying outside it, minus a penalty for long
    inter-word pauses. Speaking rate and pauses correlate with fluent speech
    but also reflect sentence complexity or thinking time — a heuristic
    proxy, not a certified fluency assessment."""
    if len(words) < 2:
        return None

    duration_seconds = words[-1].end - words[0].start
    if duration_seconds <= 0:
        return None

    words_per_minute = len(words) / duration_seconds * 60
    if words_per_minute < _FLUENT_WPM_LOW:
        rate_score = words_per_minute / _FLUENT_WPM_LOW * 100
    elif words_per_minute <= _FLUENT_WPM_HIGH:
        rate_score = 100.0
    else:
        # Decay back to 0 by roughly double the fluent band's upper bound.
        overshoot = words_per_minute - _FLUENT_WPM_HIGH
        rate_score = max(0.0, 100 - overshoot / _FLUENT_WPM_HIGH * 100)

    pause_penalty = min(
        sum(
            _PAUSE_PENALTY_PER_GAP
            for prev_word, next_word in zip(words, words[1:], strict=False)
            if next_word.start - prev_word.end > _PAUSE_GAP_SECONDS
        ),
        _MAX_PAUSE_PENALTY,
    )

    return max(0, min(100, round(rate_score - pause_penalty)))


def transcribe(
    model: Transcriber, audio_bytes: bytes, suffix: str = ".webm"
) -> TranscriptionResult:
    """Transcribe raw audio bytes (whatever format the browser recorded —
    faster-whisper decodes via bundled ffmpeg/av) to German text, plus
    pronunciation/fluency scores derived from the same decode pass. Takes
    the model as a parameter, mirroring `tutor_agent.build_tutor_graph`'s
    DI-for-testability shape."""
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, _info = model.transcribe(tmp.name, language="de", word_timestamps=True)
        # `segments` is a generator, consumed exactly once — materialize it
        # before deriving both the text and the word list from it.
        segments = list(segments)

    text = "".join(segment.text for segment in segments).strip()
    words = [word for segment in segments for word in (segment.words or [])]

    return TranscriptionResult(
        text=text,
        pronunciation_score=_pronunciation_score(words),
        fluency_score=_fluency_score(words),
    )


def transcribe_audio(audio_bytes: bytes, suffix: str = ".webm") -> TranscriptionResult:
    """Transcribe against the real, locally-cached Whisper model."""
    return transcribe(get_whisper_model(), audio_bytes, suffix=suffix)


def is_model_cached() -> bool:
    """Whether the Whisper model has already been downloaded — used by the
    admin panel's system-health view, doesn't trigger a download itself."""
    return _CACHE_DIR.is_dir() and any(_CACHE_DIR.iterdir())
