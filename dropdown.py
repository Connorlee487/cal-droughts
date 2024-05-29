import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import dash_core_components as dcc
import plotly.graph_objs as go


df = pd.read_csv("drought.csv")

fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': '1', 'value': 1},
            {'label': '2', 'value': 2},
            {'label': '3', 'value': 3}
        ],
        value=[1, 2, 3]
    ),
    html.Div(id='dd-output-container'),
    html.Div(children=[
        dcc.Graph(
            id='county_table',
            figure=fig
        ),
    ])
])

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('demo-dropdown', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)

@app.callback(
    dash.dependencies.Output('county_table', 'figure'),
    [dash.dependencies.Input('demo-dropdown', 'value')])
def update_graph(value):
    return go.Figure(data=[go.Scatter(x=[value, 2, 3], y=[4, 1, 2])])


if __name__ == '__main__':
    app.run_server(debug=True)
