import logging
import os
from typing import Set, Tuple

from mitmproxy import http
from mitmproxy.io import FlowReader

logger = logging.getLogger("mitmproxy-client")


class ServerSideReplayAddon:
    def __init__(self):
        self.is_replaying = False
        self.server_replay_files: Set[str] = set()
        self._cache: dict[Tuple[str, str], http.HTTPFlow] = {}
        self._file_metadata: dict[str, Tuple[float, int]] = {}

    def start_replaying(self, filename: str):
        if self.is_replaying:
            logger.warning("Already replaying.")
            return
        if not os.path.exists(filename):
            logger.error(f"File not found: {filename}")
            return
        self.server_replay_files.add(filename)
        self.is_replaying = True
        logger.info(f"Replaying flows from {filename}")

    def stop_replaying(self):
        if not self.is_replaying:
            logger.warning("Not currently replaying.")
            return
        self.is_replaying = False
        self.server_replay_files.clear()
        self._cache.clear()
        self._file_metadata.clear()
        logger.info("Stopped replaying.")

    def _update_cache_if_needed(self):
        if len(self._file_metadata.keys() - self.server_replay_files) > 0:
            self._file_metadata.clear()
            self._cache.clear()

        for filename in self.server_replay_files:
            if not os.path.exists(filename):
                continue

            try:
                stat = os.stat(filename)
                mtime = stat.st_mtime
                size = stat.st_size

                if (
                    metadata := self._file_metadata.get(filename, None)
                ) and metadata == (mtime, size):
                    continue
                logger.info(f"Loading/reloading replay file: {filename}")
                with open(filename, "rb") as f:
                    flow_reader = FlowReader(f)
                    for replay_flow in flow_reader.stream():
                        if isinstance(replay_flow, http.HTTPFlow):
                            key = (
                                replay_flow.request.method,
                                replay_flow.request.url,
                            )
                            self._cache[key] = replay_flow
                self._file_metadata[filename] = (mtime, size)
            except Exception as e:
                logger.error(f"Error processing replay file {filename}: {e}")

    def response(self, flow: http.HTTPFlow):
        if not self.is_replaying:
            return
        self._update_cache_if_needed()
        key = (flow.request.method, flow.request.url)
        if replay_flow := self._cache.get(key, None):
            flow.response = replay_flow.response
            logger.info(f"Replayed flow for {flow.request.url} from cache.")
