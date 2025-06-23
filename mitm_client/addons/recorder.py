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
        self.output_dir = None
        self.config = config
        self._writers: dict[str, FlowWriter] = {}

    def start_recording(self, output_dir: str):
        if self.is_recording:
            logger.warning(f"Already recording to {self.output_dir}")
            return

        self.output_dir = output_dir
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            self.is_recording = True
            logger.info(f"Starting recording to {self.output_dir}")
        except IOError as e:
            logger.error(f"Error starting recording: {e}")

    def stop_recording(self):
        if not self.is_recording:
            logger.warning("Not currently recording.")
            return

        self.is_recording = False
        for writer in self._writers.values():
            writer.fo.close()
        self._writers.clear()
        logger.info(f"Stopped recording to {self.output_dir}")
        self.output_dir = None

    def response(self, flow: http.HTTPFlow):
        if not self.is_recording or not self.output_dir:
            return

        if (not self.config.match) or any(
            pattern.match(flow.request.url)
            for pattern in map(re.compile, self.config.match)
        ):
            host = flow.request.host
            if writer := self._writers.get(host):
                writer.add(flow)
                return
            try:
                filename = os.path.join(self.output_dir, f"{host}.mitm")
                f = open(filename, "ab")
                writer = FlowWriter(f)
                self._writers[host] = writer
                writer.add(flow)
            except IOError as e:
                logger.error(f"Error writing flow to {filename}: {e}")
