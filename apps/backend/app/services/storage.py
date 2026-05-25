import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings


class LocalObjectStorage:
    def __init__(self, settings: Settings) -> None:
        self.root = Path(settings.storage_root)
        self.root.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, upload: UploadFile) -> tuple[str, Path]:
        suffix = Path(upload.filename or "source.bin").suffix.lower()
        key = f"curriculum/{uuid.uuid4()}{suffix}"
        target = self.root / key
        target.parent.mkdir(parents=True, exist_ok=True)

        with target.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                output.write(chunk)

        await upload.seek(0)
        return key, target
