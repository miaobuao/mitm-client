import webbrowser
from pathlib import Path

import gradio as gr

from mitm_client.addons import RecorderAddon, ServerSideReplayAddon
from mitm_client.app.logging_config import ActionLogHandler
from mitm_client.i18n import i18n

MITM_OUTPUT_DIR = Path("./.mitm")
MITM_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

MITM_OUTPUT_FILE_PATH = MITM_OUTPUT_DIR.joinpath("traffic.mitm")


def create_ui(
    recorder: RecorderAddon,
    replay: ServerSideReplayAddon,
    log_handler: ActionLogHandler,
):
    def _update_record_button():
        if recorder.is_recording:
            return gr.update(value=i18n("stop_recording"), variant="primary")
        else:
            return gr.update(value=i18n("start_recording"), variant="secondary")

    def _update_replay_button():
        if replay.is_replaying:
            return gr.update(value=i18n("stop_replaying"), variant="primary")
        else:
            return gr.update(value=i18n("start_replaying"), variant="secondary")

    with gr.Blocks() as app:
        gr.Markdown(f"# {i18n('app_title')}")

        with gr.Row():
            filename_input = gr.Textbox(
                label=i18n("filename_label"),
                value=MITM_OUTPUT_FILE_PATH.as_posix(),
            )

        with gr.Row():
            record_btn = gr.Button(*_update_record_button())
            replay_btn = gr.Button(*_update_replay_button())

        with gr.Row():
            log_output = gr.Textbox(
                label="Logs",
                interactive=False,
                lines=10,
                autoscroll=True,
            )

        with gr.Row():
            install_cert_button = gr.Button("Install Cert")

        @install_cert_button.click()
        def click_install_cert_button():
            webbrowser.open("http://mitm.it/")

        @record_btn.click(
            inputs=[filename_input],
            outputs=[record_btn],
        )
        def toggle_recording(filename: str):
            if recorder.is_recording:
                recorder.stop_recording()
            else:
                fpath = Path(filename).absolute().as_posix()
                recorder.start_recording(fpath)
            return _update_record_button()

        @replay_btn.click(
            inputs=[filename_input],
            outputs=[replay_btn],
        )
        def toggle_replaying(filename: str):
            if replay.is_replaying:
                replay.stop_replaying()
            else:
                fpath = Path(filename).absolute().as_posix()
                replay.start_replaying(fpath)
            return _update_replay_button()

        timer = gr.Timer(0.5)
        last_logs_str = ""

        @timer.tick(outputs=[log_output])
        def _update_logs():
            nonlocal last_logs_str
            new_logs = log_handler.get_logs()
            new_logs_str_current = "\n".join(new_logs)
            if new_logs_str_current != last_logs_str:
                last_logs_str = new_logs_str_current
                return new_logs_str_current
            return gr.update()

        @app.load(outputs=[record_btn, replay_btn, log_output])
        def _update_buttons_on_load():
            return _update_record_button(), _update_replay_button(), last_logs_str

    return app
