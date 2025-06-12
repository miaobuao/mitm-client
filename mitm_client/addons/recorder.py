import logging
import os
import re

from mitmproxy import http
from mitmproxy.io import FlowWriter

from mitm_client.config import RecorderConfig

logger = logging.getLogger("mitmproxy-client")


class RecorderAddon:
    def __init__(self, config: RecorderConfig):
        self.is_recording = False
        self.flow_writer = None
        self.file_handle = None
        self.filename = None
        self.config = config

    def start_recording(self, filename: str):
        if self.is_recording:
            logger.warning(f"Already recording to {self.filename}")
            return

        self.filename = filename
        try:
            if os.path.dirname(filename):
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.file_handle = open(self.filename, self.config.writing_mode)
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
        if not self.is_recording or not self.flow_writer:
            return

        if (not self.config.match) or any(
            pattern.match(flow.request.url)
            for pattern in map(re.compile, self.config.match)
        ):
            self.flow_writer.add(flow)
            return
