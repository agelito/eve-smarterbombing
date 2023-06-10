"""User interface"""
import gradio as gr

from smarterbombing import configuration
from smarterbombing.webui.ui_squads import render_squads

def run_webui(port: int = 42069):
    """
    Run web interface

    :param port: which port to listen to

    """
    config = configuration.load(create_if_missing=True)

    custom_css = """
    .character_container {
        padding: 8px;
        line-height: 32px;
    }
    .character_label {
        background-color: #6e00ff;
        border-radius: 6px;
        padding: 4px 8px 4px 8px;
        margin: 2px;
    }

    h4.scs {
        margin-top: 8px !important;
    }

    table.scs {
        table-layout: fixed;
        width: 100%;
        border-collapse: collapse;
    }

    table.scs tr {
        border-bottom: 1px dotted black;
    }

    table.scs th {
        text-align: left !important;
    }

    table.scs td {
        text-align: right !important;
    }

    meter.scs {
        width: 100%;
        height: 32px;
    }
    """

    with gr.Blocks(title="Smarterbombing", css=custom_css) as sb_ui:
        render_squads(sb_ui, config)

        sb_ui.queue()
        sb_ui.launch(show_api=False, server_port=port)
