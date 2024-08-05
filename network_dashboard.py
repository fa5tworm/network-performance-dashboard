import psutil
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from datetime import datetime
import threading
import time

# Function to get network stats
def get_network_stats():
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent, net_io.bytes_recv

# Initialize Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Real-Time Network Performance Dashboard"),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # in milliseconds
        n_intervals=0
    )
])

# Global data storage
x_data = []
y_data = [[], []]
last_sent = 0
last_recv = 0

@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    global last_sent, last_recv

    # Get network statistics
    bytes_sent, bytes_recv = get_network_stats()
    current_time = datetime.now()

    # Calculate the differences
    if last_sent == 0 and last_recv == 0:
        sent_diff = 0
        recv_diff = 0
    else:
        sent_diff = bytes_sent - last_sent
        recv_diff = bytes_recv - last_recv

    last_sent = bytes_sent
    last_recv = bytes_recv

    # Update data
    x_data.append(current_time)
    y_data[0].append(sent_diff)
    y_data[1].append(recv_diff)

    # Create the plot
    fig = go.Figure()

    # Add sent data trace
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data[0],
        mode='lines+markers',
        name='Bytes Sent',
        line=dict(color='blue')
    ))

    # Add received data trace
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data[1],
        mode='lines+markers',
        name='Bytes Received',
        line=dict(color='green')
    ))

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Bytes',
        xaxis=dict(tickformat='%H:%M:%S', type='date')
    )

    return fig

def run_app():
    app.run_server(debug=False)

if __name__ == '__main__':
    # Run Dash app in a separate thread
    threading.Thread(target=run_app).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
