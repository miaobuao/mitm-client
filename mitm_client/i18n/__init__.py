import gradio as gr

from .en import LANG as en
from .zh import LANG as zh

i18n = gr.I18n(
    en=en,
    zh=zh,
)
