import os
from datetime import datetime
import asyncio
from ignis.services.recorder import RecorderService, RecorderConfig
from ignis.command_manager import CommandManager
from ignis.services.recorder.service import RecorderPortalCaptureCanceled
from .send_notification import send_notification
from user_settings import user_settings

command_manager = CommandManager.get_default()
recorder = RecorderService.get_default()
last_recording_path = None
recording_indicator_instance = None

def set_indicator(indicator):
    global recording_indicator_instance
    recording_indicator_instance = indicator

def _on_recording_started(service):
    global last_recording_path
    if recording_indicator_instance:
        recording_indicator_instance.set_paused(False)
        if user_settings.interface.bar.modules.recording_indicator != "never":
            recording_indicator_instance.start_timer()
            
    send_notification("Recording Started", f"Recording to: {last_recording_path}")

def _on_recording_stopped(service):
    global last_recording_path
    if recording_indicator_instance:
        recording_indicator_instance.stop_timer()
    if last_recording_path:
        send_notification("Recording Stopped", f"Recording saved to: {last_recording_path}")
    last_recording_path = None
    
def _update_pause_state():
    if recording_indicator_instance:
        recording_indicator_instance.set_paused(recorder.is_paused)

async def _start_recording_task(source: str, file_path: str, **kwargs):
    global last_recording_path
    
    rec_config = RecorderConfig(
        source=source,
        path=file_path,
        **kwargs
    )
    
    try:
        await recorder.start_recording(config=rec_config)
    except RecorderPortalCaptureCanceled:
        if recording_indicator_instance:
            recording_indicator_instance.stop_timer()
        last_recording_path = None
        send_notification("Recording Canceled", "The desktop portal capture was canceled.")
    except Exception as e:
        last_recording_path = None
        send_notification("Recording Error", f"An unexpected error occurred: {str(e)}")

def _record_source(source: str, *args: str, **kwargs):
    global last_recording_path
    
    if not recorder.is_available:
        send_notification("No recorder", "gpu-screen-recorder was not found.")
        return
    
    if recorder.active:
        recorder.stop_recording()
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.expanduser(f"~/Videos/recording_{timestamp}.mp4")
    last_recording_path = file_path
    
    asyncio.create_task(_start_recording_task(source=source, file_path=file_path, **kwargs))

def stop_recording():
    if recorder.active:
        recorder.stop_recording()
    
def pause_recording():
    if recorder.active and not recorder.is_paused:
        recorder.pause_recording()
        _update_pause_state()

def unpause_recording():
    if recorder.active and recorder.is_paused:
        recorder.continue_recording()
        _update_pause_state()

def record_screen(*args: str):
    _record_source("screen", audio_devices=["default_output"],  *args)

def record_portal(*args: str):
    _record_source("portal", *args)

async def _record_region_task():
    """Selects a region using 'slurp' and starts recording it."""
    try:
        if recorder.active:
            recorder.stop_recording()
            return

        send_notification("Region Selection", "Please select a region to record.")
        
        proc = await asyncio.create_subprocess_exec(
            "slurp",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            if proc.returncode == 127:
                send_notification("Dependency Missing", "The 'slurp' tool is required for region recording but was not found.")
            else:
                send_notification("Region Selection Canceled", "No region was selected or an error occurred.")
            return

        region_str = stdout.decode().strip()
        if not region_str:
            send_notification("Region Selection Canceled", "No region was selected.")
            return
        
        # Reformat the region string from 'X,Y WxH' to 'WxH+X+Y'
        xy, wh = region_str.split(" ")
        x, y = xy.split(",")
        reformatted_region = f"{wh}+{x}+{y}"

        _record_source(source="region", region=reformatted_region)
        
    except FileNotFoundError:
        send_notification("Dependency Missing", "The 'slurp' tool is required for region recording but was not found.")
    except Exception as e:
        send_notification("Region Selection Error", f"An unexpected error occurred: {str(e)}")

def record_region(*args: str):
    asyncio.create_task(_record_region_task())

def setup_recorder_commands():
    command_manager.add_command(
        command_name="recorder-record-screen",
        callback=record_screen,
    )
    
    command_manager.add_command(
        command_name="recorder-record-portal",
        callback=record_portal,
    )

    command_manager.add_command(
        command_name="recorder-record-region",
        callback=record_region,
    )

def setup_recorder_signals():
    recorder.connect("recording_started", _on_recording_started)
    recorder.connect("recording_stopped", _on_recording_stopped)

setup_recorder_commands()
setup_recorder_signals()