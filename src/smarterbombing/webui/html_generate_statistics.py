import pandas as pd

def generate_compound_statistics_html(compound: pd.DataFrame):
    """
    Generate a HTML table displaying compound site statistics.

    :param compound: compound site statistics

    :returns: a html string

    """

    efficiency = compound['time_efficiency']
    efficiency_percent = int(efficiency * 100)

    html = f"""
    <h4 class="scs">Average Site Efficiency</h4>
    <meter class="scs" max="1" low="0.5" optimum="1.0" high="0.7" value="{efficiency}">Efficiency</meter>
    <table class="scs">
        <tr>
            <th scope="row">Efficiency</th>
            <td>{efficiency_percent}%</td>
        </tr>
        <tr>
            <th scope="row">Total Time</th>
            <td>{compound['total_time']}</td>
        </tr>
        <tr>
            <th scope="row">Downtime</th>
            <td>{compound['total_downtime']}</td>
        </tr>
        <tr>
            <th scope="row">Effective Time</th>
            <td>{compound['total_effective_time']}</td>
        </tr>
        <tr>
            <th scope="row">Average Time</th>
            <td>{compound['average_time']}</td>
        </tr>
        <tr>
            <th scope="row">Average Downtime</th>
            <td>{compound['average_downtime']}</td>
        </tr>
        <tr>
            <th scope="row">Damage Per Second</th>
            <td>{compound['damage_per_second']}</td>
        </tr>
    </table>"""

    return html
