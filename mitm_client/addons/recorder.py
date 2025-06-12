import logging
import os

from mitmproxy import http
from mitmproxy.io import FlowWriter

logger = logging.getLogger("mitmproxy-client")


class RecorderAddon:
    def __init__(self):
        self.is_recording = False
        self.flow_writer = None
        self.file_handle = None
        self.filename = None

    def start_recording(self, filename: str):
        if self.is_recording:
            logger.warning(f"Already recording to {self.filename}")
            return

        self.filename = filename
        try:
            if os.path.dirname(filename):
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.file_handle = open(self.filename, "wb")
            self.flow_writer = FlowWriter(self.file_handle)
            self.is_recording = True
            logger.info(f"Starting recording to {self.filename}")
        except IOError as e:
            logger.error(f"Error starting recording: {e}")

    def stop_recording(self):
        if not self.is_recording:
            logger.warning("Not currently recording.")
            return

        self.is_recording = False
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
        self.flow_writer = None
        logger.info(f"Stopped recording to {self.filename}")

    def response(self, flow: http.HTTPFlow):
        if self.is_recording and self.flow_writer:
            self.flow_writer.add(flow)
