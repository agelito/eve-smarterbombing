"""User interface"""
import gradio as gr

from smarterbombing.app_live import AppLive
from smarterbombing.app_offline import AppOffline
from smarterbombing.configuration import load_configuration
from smarterbombing.webui.ui_configuration import render_configuration
from smarterbombing.webui.ui_live import render_live
from smarterbombing.webui.ui_offline_analysis import render_offline_analysis

CONFIGURATION_PATH = 'configuration.json'

def run_webui(port: int = 42069):
    """Run web interface"""
    configuration = load_configuration(CONFIGURATION_PATH)

    app_offline = AppOffline(configuration)
    app_live = AppLive(configuration)
    app_live.open_logs()

    with gr.Blocks(title="Smarterbombing") as sb_ui:
        with gr.Tab('Live'):
            render_live(sb_ui, app_live)

        with gr.Tab('Offline Analysis'):
            render_offline_analysis(app_offline, configuration)

        with gr.Tab('Configuration'):
            render_configuration(configuration, CONFIGURATION_PATH)

    sb_ui.queue()
    sb_ui.launch(show_api=False, server_port=port)

    app_live.close_logs()
