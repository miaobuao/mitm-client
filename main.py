from pathlib import Path

from mitm_client.addons import RecorderAddon, ServerSideReplayAddon
from mitm_client.app.logging_config import setup_logging
from mitm_client.app.proxy_runner import MitmProxyRunner
from mitm_client.app.ui import create_ui
from mitm_client.config import load_config
from mitm_client.i18n import i18n


def main():
    app_config = load_config(Path("config.json5"))
    log_handler = setup_logging()
    recorder = RecorderAddon(app_config.recorder)
    replay = ServerSideReplayAddon(app_config.replay)
    proxy_runner = MitmProxyRunner(recorder, replay)
    proxy_runner.start()

    ui = create_ui(recorder, replay, log_handler)
    ui.launch(i18n=i18n)

    print("UI closed. Shutting down mitmproxy...")
    proxy_runner.stop()


if __name__ == "__main__":
    main()
