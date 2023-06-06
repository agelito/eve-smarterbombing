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

    def _update_site_statistics():
        app_live.update_site_statistics()
        value = app_live.site_statistics

        if value.empty:
            return gr.update(visible=False)

        return gr.update(value=value, visible=True)

    def _update_compound_site_statistics():
        app_live.update_compound_site_statistics()
        value = app_live.site_compound_statistics

        if value.empty:
            return gr.update(visible=False)

        return gr.update(value=value, visible=True)

    def _reload_files():
        app_live.open_logs()

        return _update_open_log_files()

    def _close_files():
        app_live.close_logs()

        return _update_open_log_files()

    def _clear_data():
        app_live.clear_data()

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
            compound_site_statistics = gr.DataFrame(label='Compound Site Statistics', interactive=False)
            site_statistics = gr.DataFrame(label='Site Statistics', interactive=False)

    gr.Markdown(value='_Graphs and statistics will appear once started ratting._')

    with gr.Column():
        with gr.Accordion('Diagnostics', open=False):
            with gr.Row():
                reload_files = gr.Button(value='Reload Files')
                close_files = gr.Button(value='Close Files')
                clear_data = gr.Button(value='Clear Data')

            log_timestamp = gr.Markdown(value='Most recent log timestamp: None')
            open_logfiles = gr.Dataframe(value=[], label='Open Logs', visible=False)

            reload_files.click(fn=_reload_files, outputs=open_logfiles)
            close_files.click(fn=_close_files, outputs=open_logfiles)
            clear_data.click(fn=_clear_data)

    sb_ui.load(_update_app, None, None, every=1)
    sb_ui.load(_update_log_timestamp_text, None, log_timestamp, every=5)
    sb_ui.load(_update_open_log_files, None, open_logfiles, every=5)

    sb_ui.load(_update_outgoing_hostile_dps, None, dps_out_h, every=1)
    sb_ui.load(_update_outgoing_friendly_dps, None, dps_out_f, every=1)
    sb_ui.load(_update_incoming_hostile_dps, None, dps_in_h, every=1)
    sb_ui.load(_update_incoming_friendly_dps, None, dps_in_f, every=1)
    sb_ui.load(_update_site_statistics, None, site_statistics, every=5)
    sb_ui.load(_update_compound_site_statistics, None, compound_site_statistics, every=5)
