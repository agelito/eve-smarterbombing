"""Squads interface"""
import gradio as gr

from smarterbombing import configuration
from smarterbombing.app.squad import Squad
from smarterbombing.webui.html_generate_statistics import generate_compound_statistics_html

def _update_aggregators(app_squad: Squad):
    app_squad.read_and_aggregate_data()

    compound_site_statistics = app_squad.get_compound_site_statistics()
    html_statistics = generate_compound_statistics_html(compound_site_statistics)

    return [
        gr.update(value=app_squad.get_outgoing_hostile_damage_graph()),
        gr.update(value=app_squad.get_incoming_hostile_damage_graph()),
        gr.update(value=html_statistics),
    ]

def _reset_input_value():
    return gr.update(value='')

def _reinitialize_readers(app_squad: Squad):
    app_squad.initialize_readers()
    return app_squad.get_open_files()

def _render_squad_graphs(config: dict):
    graph_width = configuration.get_graph_width(config)

    with gr.Row(variant='compact'):
        dps_out_h = gr.LinePlot(
            x_title='Time',
            x='timestamp',
            y_title='DPS',
            y='damage',
            color='character',
            title='Outgoing Damage',
            interactive=False,
            width=graph_width)

        dps_in_h = gr.LinePlot(
            x_title='Time',
            x='timestamp',
            y_title='DPS',
            y='damage',
            color='character',
            title='Incoming Damage',
            interactive=False,
            width=graph_width)

    with gr.Row(variant='compact'):
        with gr.Column(variant='compact'):
            site_compound = gr.HTML()
            gr.Markdown(
                        "💡 _The average data will populate after starting at least two sites._"
                    )

    return [dps_out_h, dps_in_h, site_compound]

def _render_squad_configuration(config: dict, app_squad: Squad, squad: dict):
    def _squad_member_list(squad):
        if len(squad['characters']) == 0:
            return '⚠ No characters'

        characters = squad['characters']
        characters = map(lambda c: f'<span class="character_label">{c}</span>', characters)

        return f'<div class="character_container">{" ".join(characters)}</div>'

    def _add_character_to_squad(character):
        if character in squad['characters']:
            squad['characters'].remove(character)
        else:
            squad['characters'].append(character)

        configuration.save(config)

        return _squad_member_list(squad)

    with gr.Accordion(label='Squad Configuration', open=len(squad['characters']) == 0):
        with gr.Row(variant='compact'):
            with gr.Column():
                character_input = gr.Textbox(label='➕ Add/Remove Character')
                gr.Markdown(
                    "💡 _Type a character name and press enter to add or remove the character._"
                )
            with gr.Column(scale=2):
                character_list = gr.HTML(_squad_member_list(squad))

        open_log_files = gr.Dataframe(label='Open Logs', value=app_squad.get_open_files())
        reload_logs = gr.Button(value='Reload Logs', variant='secondary')

        reload_logs.click(lambda: _reinitialize_readers(app_squad), outputs=open_log_files)

        character_input.submit(_add_character_to_squad,
                                inputs=character_input,
                                outputs=character_list,
        ).then(_reset_input_value,
               outputs=character_input
        ).then(lambda: _reinitialize_readers(app_squad), outputs=open_log_files)

def render_squad(sb_ui: gr.Blocks, config: dict, squad: dict):
    """
    Render squad UI

    :param sb_ui: user interface
    :param config: configuration
    :param squad: squad

    """

    squad_name = squad['squad_name']

    app_squad = Squad(squad_name, squad['characters'], config)
    app_squad.initialize_aggregators()
    app_squad.initialize_readers()

    app_squad.read_and_aggregate_data()

    with gr.Tab(squad_name):
        _render_squad_configuration(config, app_squad, squad)
        graphs = _render_squad_graphs(config)

    sb_ui.load(lambda: _update_aggregators(app_squad), every=1, outputs=graphs)
