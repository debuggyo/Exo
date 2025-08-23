import asyncio
from ignis.services.recorder import RecorderService, RecorderConfig

recorder = RecorderService.get_default()

rec_config = RecorderConfig(
    source="portal",
    path="path/to/file",
)