"""Text-to-speech wrapper for Conversation Mode.

Uses Piper via its official prebuilt CLI binary (github.com/rhasspy/piper
releases) rather than the `piper-tts` Python package — `piper-phonemize` (a
transitive native dependency of that package) publishes no Linux ARM64
wheel, which is exactly the platform this backend's Docker image builds for
on Apple Silicon. The binary release bundles the same onnxruntime +
espeak-ng-data and ships a `linux_aarch64` build, so this keeps TTS fully
local with no API key on this platform too. Both the binary and the voice
model are downloaded once and cached locally on first use — same lazy-cache
shape as fastembed's embedding model and the Whisper model.
"""
import platform
import subprocess
import tarfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Protocol

import httpx

from app.core.config import get_settings

settings = get_settings()

_CACHE_DIR = Path(__file__).resolve().parents[3] / ".piper_cache"
_VOICES_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
_PIPER_RELEASE = "2023.11.14-2"
_PIPER_RELEASES_BASE_URL = f"https://github.com/rhasspy/piper/releases/download/{_PIPER_RELEASE}"


class Synthesizer(Protocol):
    """What `synthesize` needs from a voice — narrow enough that tests can
    pass a fake without downloading a real binary or voice model."""

    def synthesize(self, text: str) -> bytes: ...


def _download(url: str, dest: Path) -> None:
    with httpx.stream("GET", url, follow_redirects=True, timeout=120.0) as response:
        response.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)


def _piper_platform_tag() -> str:
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        arch = "aarch64"
    elif machine in ("x86_64", "amd64"):
        arch = "x86_64"
    else:
        raise RuntimeError(f"No Piper CLI build known for platform.machine()={machine!r}")
    return f"linux_{arch}"


def _ensure_piper_binary() -> Path:
    binary_path = _CACHE_DIR / "piper" / "piper"
    if binary_path.exists():
        return binary_path

    _CACHE_DIR.mkdir(exist_ok=True)
    tag = _piper_platform_tag()
    archive_path = _CACHE_DIR / f"piper_{tag}.tar.gz"
    _download(f"{_PIPER_RELEASES_BASE_URL}/piper_{tag}.tar.gz", archive_path)
    with tarfile.open(archive_path) as tar:
        tar.extractall(_CACHE_DIR)  # noqa: S202 — trusted, pinned release URL
    archive_path.unlink()
    binary_path.chmod(0o755)
    return binary_path


def _voice_repo_path(voice_name: str) -> str:
    """"de_DE-thorsten-medium" -> "de/de_DE/thorsten/medium/de_DE-thorsten-medium"."""
    locale, rest = voice_name.split("-", 1)
    speaker, quality = rest.rsplit("-", 1)
    lang = locale.split("_")[0]
    return f"{lang}/{locale}/{speaker}/{quality}/{voice_name}"


def _ensure_voice_files(voice_name: str) -> Path:
    """Downloads the .onnx model and its .onnx.json config side by side —
    Piper looks up the config at `<model_path>.json` by convention."""
    _CACHE_DIR.mkdir(exist_ok=True)
    model_path = _CACHE_DIR / f"{voice_name}.onnx"
    config_path = _CACHE_DIR / f"{voice_name}.onnx.json"

    repo_path = _voice_repo_path(voice_name)
    for path, suffix in ((model_path, ".onnx"), (config_path, ".onnx.json")):
        if not path.exists():
            _download(f"{_VOICES_BASE_URL}/{repo_path}{suffix}", path)
    return model_path


@dataclass
class PiperCliVoice:
    binary_path: Path
    model_path: Path

    def synthesize(self, text: str) -> bytes:
        result = subprocess.run(
            [str(self.binary_path), "--model", str(self.model_path), "--output_file", "-"],
            input=text.encode("utf-8"),
            capture_output=True,
            check=True,
        )
        return result.stdout


@lru_cache
def get_piper_voice() -> PiperCliVoice:
    binary_path = _ensure_piper_binary()
    model_path = _ensure_voice_files(settings.PIPER_VOICE)
    return PiperCliVoice(binary_path=binary_path, model_path=model_path)


def synthesize(voice: Synthesizer, text: str) -> bytes:
    """Synthesize `text` (German) to WAV bytes. Takes the voice as a
    parameter, mirroring `tutor_agent.build_tutor_graph`'s
    DI-for-testability shape."""
    return voice.synthesize(text)


def synthesize_speech(text: str) -> bytes:
    """Synthesize against the real, locally-cached Piper voice."""
    return synthesize(get_piper_voice(), text)


def is_model_cached() -> bool:
    """Whether the Piper binary + voice have already been downloaded — used
    by the admin panel's system-health view, doesn't trigger a download."""
    return (_CACHE_DIR / "piper" / "piper").exists() and (
        _CACHE_DIR / f"{settings.PIPER_VOICE}.onnx"
    ).exists()
