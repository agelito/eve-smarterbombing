"""Squads interface"""
import gradio as gr

from smarterbombing import configuration
from smarterbombing.webui.ui_squad import render_squad

def render_squads(sb_ui: gr.Blocks, config: dict):
    """
    Render squads user interface

    :param sb_ui: the Blocks user interface object
    :param config: the configuration

    """

    squads = configuration.get_squads(config)

    for squad_index in range(len(squads)):
        squad = config['squads'][squad_index]
        render_squad(sb_ui, config, squad)
