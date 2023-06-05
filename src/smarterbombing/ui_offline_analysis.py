"""Offline analysis UI"""
import gradio as gr
from smarterbombing.analysis import average_dps_per_character_melt
from smarterbombing.app_offline import AppOffline

from smarterbombing.logs import find_all_dates

def render_offline_analysis(configuration):
    """Render the offline analysis UI"""
    offline_app = AppOffline(configuration)

    def _damage_over_time_hostile():
        return average_dps_per_character_melt(offline_app.damage_over_time_hostile())

    def _damage_over_time_friendly():
        return average_dps_per_character_melt(offline_app.damage_over_time_friendly())

    def _damage_over_time_incoming_hostile():
        return average_dps_per_character_melt(offline_app.damage_over_time_incoming_hostile())

    def _damage_over_time_incoming_friendly():
        return average_dps_per_character_melt(offline_app.damage_over_time_incoming_friendly())

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
