import asyncio
import threading

from mitmproxy.master import Master
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster


class MitmProxyRunner:
    def __init__(self, *addons):
        self.addons = addons
        self.master: Master | None = None
        self.thread = None

    def run_mitmproxy(self):
        async def run():
            opts = Options(
                listen_host="0.0.0.0",
                listen_port=8080,
                http2=False,
            )
            self.master = DumpMaster(opts)
            self.master.addons.add(*self.addons)
            await self.master.run()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run_mitmproxy, daemon=True)
            self.thread.start()
            print("mitmproxy started.")

    def stop(self):
        if self.master:
            self.master.shutdown()
            print("mitmproxy shutting down.")
        if self.thread and self.thread.is_alive():
            self.thread.join()
            print("mitmproxy thread joined.")
