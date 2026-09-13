"""One-off batch job: synthesizes audio for every seeded ListeningScript that
doesn't have one yet, and uploads it to object storage.

Run once after migrating (and again whenever new listening scripts are
seeded) via:

    docker compose exec backend python -m app.ai.speech.synthesize_listening_audio

Idempotent — only scripts with `audio_object_key IS NULL` are processed, so
re-running is safe. If this step is skipped, `ListeningService.get_audio`
self-heals by synthesizing on first request instead — this script only
avoids that per-script first-request latency.
"""
import asyncio
import logging

from sqlalchemy import select

from app.ai.speech.tts import synthesize_speech
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.object_store.minio_client import get_object_store
from app.models.listening_script import ListeningScript

logger = logging.getLogger(__name__)


async def synthesize_pending_scripts() -> int:
    """Synthesizes and uploads audio for every script missing it. Returns
    the number of scripts synthesized."""
    object_store = get_object_store()
    count = 0
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ListeningScript).where(ListeningScript.audio_object_key.is_(None))
        )
        scripts = list(result.scalars().all())

        for script in scripts:
            key = f"listening/{script.id}.wav"
            audio_bytes = synthesize_speech(script.script_text)
            object_store.put_object(key, audio_bytes, "audio/wav")
            script.audio_object_key = key
            count += 1

        await session.commit()
    return count


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    count = asyncio.run(synthesize_pending_scripts())
    print(f"Synthesized audio for {count} listening script(s).")


if __name__ == "__main__":
    main()
