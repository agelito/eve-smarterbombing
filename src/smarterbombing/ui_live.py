"""Live UI"""
import gradio as gr
import pandas as pd
from smarterbombing.analysis import average_dps_per_character_melt

from smarterbombing.app_live import AppLive

def render_live(sb_ui: gr.Blocks, configuration):
    """Render live UI"""
    app_live = AppLive(configuration)
    app_live.open_logs()

    def _update_app():
        app_live.update()

    def _update_log_timestamp_text():
        return gr.update(value=f'Log Timestamp: {app_live.most_recent_timestamp}')

    def _update_open_log_files():
        if not app_live.is_logs_open():
            return gr.update(visible=False)

        log_table = list(map(
            lambda log: { 'File': log.filename, 'Character': log.character },
            app_live.logs
        ))

        return gr.update(value=pd.DataFrame(log_table), visible=True)

    def _update_outgoing_hostile_dps():
        if app_live.outgoing_hostile_damage.empty:
            return gr.update(visible=False)

        value = average_dps_per_character_melt(app_live.outgoing_hostile_damage)

        return gr.update(value=value, visible=True)

    def _update_outgoing_friendly_dps():
        if app_live.outgoing_friendly_damage.empty:
            return gr.update(visible=False)

        value = average_dps_per_character_melt(app_live.outgoing_friendly_damage)

        return gr.update(value=value, visible=True)

    def _update_incoming_hostile_dps():
        if app_live.incoming_hostile_damage.empty:
            return gr.update(visible=False)

        value = average_dps_per_character_melt(app_live.incoming_hostile_damage)

        return gr.update(value=value, visible=True)

    def _update_incoming_friendly_dps():
        if app_live.incoming_friendly_damage.empty:
            return gr.update(visible=False)

        value = average_dps_per_character_melt(app_live.incoming_friendly_damage)

        return gr.update(value=value, visible=True)

    with gr.Column():
        with gr.Row():
            dps_out_h = gr.LinePlot(
                x_title='Time',
                x='timestamp',
                y_title='DPS',
                y='damage',
                color='character',
                title='Outgoing Damage',
                interactive=False,
                visible=False,
                width=530)
            
            dps_in_h = gr.LinePlot(
                x_title='Time',
                x='timestamp',
                y_title='DPS',
                y='damage',
                color='character',
                title='Incoming Damage',
                interactive=False,
                visible=False,
                width=530)
            
        with gr.Row():
            dps_out_f = gr.LinePlot(
                x_title='Time',
                x='timestamp',
                y_title='DPS',
                y='damage',
                color='character',
                title='Outgoing Damage (Friendly)',
                interactive=False,
                visible=False,
                width=530)

            dps_in_f = gr.LinePlot(
                x_title='Time',
                x='timestamp',
                y_title='DPS',
                y='damage',
                color='character',
                title='Incoming Damage (Friendly)',
                interactive=False,
                visible=False,
                width=530)

    with gr.Column():
        with gr.Accordion('Diagnostics', open=False):
            log_timestamp = gr.Markdown(value='Most recent log timestamp: None')
            open_logfiles = gr.Dataframe(value=[], label='Open Logs', visible=False)

    sb_ui.load(_update_app, None, None, every=1)
    sb_ui.load(_update_log_timestamp_text, None, log_timestamp, every=5)
    sb_ui.load(_update_open_log_files, None, open_logfiles, every=5)

    sb_ui.load(_update_outgoing_hostile_dps, None, dps_out_h, every=1)
    sb_ui.load(_update_outgoing_friendly_dps, None, dps_out_f, every=1)
    sb_ui.load(_update_incoming_hostile_dps, None, dps_in_h, every=1)
    sb_ui.load(_update_incoming_friendly_dps, None, dps_in_f, every=1)
