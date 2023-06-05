"""User interface"""
import gradio as gr

from smarterbombing.analysis import average_dps_per_character_melt
from smarterbombing.configuration import load_configuration, save_configuration
from smarterbombing.app_offline import AppOffline
from smarterbombing.logs import find_all_dates

CONFIGURATION_PATH = 'configuration.json'

configuration = load_configuration(CONFIGURATION_PATH)

offline_app = AppOffline(configuration)

def _character_list(config):
    return ', '.join(config['characters'])

def _add_character(character_name):
    characters = configuration['characters']
    characters.append(character_name)
    save_configuration(configuration, CONFIGURATION_PATH)
    print(f'added character -> {character_name}')

    return _character_list(configuration)

def _change_log_directory(new_log_directory):
    configuration['log_directory'] = new_log_directory
    save_configuration(configuration, CONFIGURATION_PATH)
    print(f'changed log_directory -> {new_log_directory}')

def _damage_over_time_hostile():
    return average_dps_per_character_melt(offline_app.damage_over_time_hostile())

def _damage_over_time_friendly():
    return average_dps_per_character_melt(offline_app.damage_over_time_friendly())

def _damage_over_time_incoming_hostile():
    return average_dps_per_character_melt(offline_app.damage_over_time_incoming_hostile())

def _damage_over_time_incoming_friendly():
    return average_dps_per_character_melt(offline_app.damage_over_time_incoming_friendly())

with gr.Blocks(title="Smarterbombing") as sb_ui:
    with gr.Tab('Offline Analysis'):
        with gr.Column():
            with gr.Row():
                gr.Markdown("""### Offline Analysis
                Look back at and analyse performance from old log files. This can be used to 
                compare statistics from various ratting sessions. Select a date from the drop
                down menu on the right and wait a moment for data to be crunched by the system.""")

                log_dates = find_all_dates(configuration['log_directory'])
                selected_date = gr.Dropdown(choices=log_dates, label='Date')

            with gr.Accordion(label='Sessions'):
                sessions = gr.DataFrame(
                    label='Sessions',
                    headers=['Date', 'Start', 'End'],
                    interactive=False)

        with gr.Column():
            with gr.Row():
                dps_out_h = gr.LinePlot(
                    x_title='Time',
                    x='timestamp',
                    y_title='DPS',
                    y='damage',
                    color='character',
                    title='Outgoing Damage',
                    width=530)

                dps_out_f = gr.LinePlot(
                    x_title='Time',
                    x='timestamp',
                    y_title='DPS',
                    y='damage',
                    color='character',
                    title='Outgoing Damage (Friendly)',
                    width=530)
            with gr.Row():
                dps_in_h = gr.LinePlot(
                    x_title='Time',
                    x='timestamp',
                    y_title='DPS',
                    y='damage',
                    color='character',
                    title='Incoming Damage',
                    width=530)

                dps_in_f = gr.LinePlot(
                    x_title='Time',
                    x='timestamp',
                    y_title='DPS',
                    y='damage',
                    color='character',
                    title='Incoming Damage (Friendly)',
                    width=530)

        selected_date.change(
            offline_app.load_at_date,
            inputs=[selected_date],
            outputs=[sessions],
        ).then(
            _damage_over_time_hostile,
            outputs=dps_out_h
        ).then(
            _damage_over_time_friendly,
            outputs=dps_out_f
        ).then(
            _damage_over_time_incoming_hostile,
            outputs=dps_in_h
        ).then(
            _damage_over_time_incoming_friendly,
            outputs=dps_in_f
        )

    with gr.Tab('Configuration'):
        log_directory = gr.Textbox(
            value=configuration['log_directory'],
            label="EVE Online Log Directory")
        log_directory.submit(fn=_change_log_directory, inputs=[log_directory])

        add_character = gr.Textbox(
            placeholder='Character name',
            label='Add Character')

        gr.Markdown('### Characters')
        character_list = gr.Markdown(_character_list(configuration))

        add_character.submit(fn=_add_character, inputs=[add_character], outputs=[character_list])

sb_ui.queue()
sb_ui.launch(show_api=False, server_port=42069)
