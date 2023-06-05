"""User interface"""
import gradio as gr

from smarterbombing.configuration import load_configuration
from smarterbombing.ui_configuration import render_configuration
from smarterbombing.ui_live import render_live
from smarterbombing.ui_offline_analysis import render_offline_analysis

CONFIGURATION_PATH = 'configuration.json'

configuration = load_configuration(CONFIGURATION_PATH)

with gr.Blocks(title="Smarterbombing") as sb_ui:
    with gr.Tab('Live'):
        render_live(sb_ui, configuration)

    with gr.Tab('Offline Analysis'):
        render_offline_analysis(configuration)

    with gr.Tab('Configuration'):
        render_configuration(configuration, CONFIGURATION_PATH)

sb_ui.queue()
sb_ui.launch(show_api=False, server_port=42069)
