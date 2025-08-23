import asyncio
from ignis import utils

def send_notification(summary: str, body: str = None):
    if body:
        asyncio.create_task(utils.exec_sh_async(f"notify-send -a 'Exo' '{summary}' '{body}'"))
    else:
        asyncio.create_task(utils.exec_sh_async(f"notify-send -a 'Exo' '{summary}'"))