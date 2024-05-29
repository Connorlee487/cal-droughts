import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json
import time
import datetime
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from flask_caching.backends import FileSystemCache
from dash_extensions.callback import CallbackCache, Trigger
app = dash.Dash(prevent_initial_callbacks=True)

app.title = 'California Drought'

# Create (server side) disk cache.
cc = CallbackCache(cache=FileSystemCache(cache_dir="server_cache_dir"))

def geojson():
    f = open('geojson-counties-fips.json',)
    return json.load(f)

def droughts():
    return pd.read_csv("dm_export_20100101_20200901.csv", dtype={"FIPS": str})

def getMonthRange(df):
    return sorted(pd.DatetimeIndex(df['releaseDate']).month.unique())

def getDayRange(df):
    return sorted(pd.DatetimeIndex(df['releaseDate']).day.unique())

def getYearsRange(df):
    return sorted(pd.DatetimeIndex(df['releaseDate']).year.unique())

def getDroughtLevel():
    return ['NONE', 'D0', 'D1', 'D2', 'D3', 'D4']

def getSelectedRecord(df, year, month, day):
    date = datetime.datetime(year, month, day)
    qDateStr = date.strftime('%Y%m%d')
    return df.query('releaseDate == @qDateStr')[['FIPS','Value']]

def getTable(hd, countyData):
    return go.Figure(data=[go.Table(
        header=dict(
            values=[hd[0],hd[2],hd[3],hd[5],hd[6],hd[7],hd[8],hd[9],hd[10],hd[11]],
            line_color='darkslategray',
            fill_color='grey',
            align='left',
            font=dict(color='white', size=14)),
        cells=dict(
            values=[countyData.releaseDate, countyData.county, countyData.state, countyData.D0, countyData.D1, countyData.D2, countyData.D3, countyData.D4, countyData.validStart, countyData.validEnd],
            line_color='darkslategray',
            align = ['left', 'center'],
            font = dict(color = 'darkslategray', size = 12)
        ))
    ])

def getHeatMap(df, selectedDate, valueGraph):
    df['Value'] = 100 - df[valueGraph]
    selected_heatmap_data = getSelectedRecord(df,selectedDate.year, selectedDate.month, selectedDate.day)
    fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=selected_heatmap_data['FIPS'], z=selected_heatmap_data['Value'],
                                        colorscale="OrRd",
                                        zmin=0,
                                        zmax=100,
                                        marker_opacity=0.5,
                                        marker_line_width=0.1
                                        ))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig


counties = geojson()
df = droughts()
#df['Value'] = 100 - df['NONE']
df2 = pd.read_csv("national_pre.csv")
#ADAWDA
tempDf = pd.read_csv("nationalDrought.csv")
tempDf['ValidStart'] = pd.to_datetime(tempDf['ValidStart'])
tempDf = tempDf.sort_values(by=['ValidStart'], ascending=True)
#ADAWDAD
nationalDry = pd.read_csv("national_dry.csv")
allCounties = sorted(df['county'].unique())
percentD = getDroughtLevel()
first_county = allCounties[0]
countyData = df.query('county==@first_county')
#print(countyData.head(5))
allDates = sorted(pd.DatetimeIndex(pd.to_datetime(df['releaseDate'].astype(str), format='%Y%m%d')).unique())

#PADKAPDOWA
tempGraphhh = px.line(tempDf, x='ValidStart', y='hasDry_pre', color='bound', title=f'Prediction Training Graph')
#APDMAPDOPAW

datemarket = {}
for idx,d in enumerate(allDates):
    if idx % 70 == 0 or idx == len(allDates) - 1:
        markervalue = {}
        markervalue['label'] = d.strftime('%Y-%m-%d')
        markervalue['style'] = {'color': '#FFFFFF'}
        datemarket[f'{idx}'] = markervalue

defaultDate = allDates[len(allDates)-1]
defaultDateStr = defaultDate.strftime('%Y-%m-%d')

tempDate = defaultDate
tempPercent = 'D0'

heatmap = getHeatMap(df, tempDate, tempPercent)

county_trend = px.line(countyData, x="validStart", y="D0", title=f'Drought data trend in {first_county}')
county_trendA = px.line(countyData, x="releaseDate", y="D1", title=f'Drought data trend in {first_county}')


national = px.line(df2, x="ValidStart", y="hasDry", title='Line Graph For Now')
nationalDryGraph = px.line(nationalDry, y='hasDry', title='Date v. Drought %')

colors = {
    'background': '#808080',
    'text': '#FFFFFF',
    'heatmap': '#FFFFFF',
    'headerColor' : 'FFFFFF',
    'rowEvenColor' : 'lightgrey',
    'rowOddColor' : 'white'
}
hd = list(df.columns)


county_table = getTable(hd, countyData)

app.layout = html.Div(style={'backgroundColor': colors['background'],'box-sizing': 'border-box'}, children=[
    html.H1(
        children='US Droughts (2010 - 2020)',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(children=[
        html.H2(id='heatmap_selected_date',
                children=f'Heatmap on {defaultDateStr}',
                style={
                    'textAlign': 'center',
                    'color': colors['heatmap']
                }
                ),
        html.Div(children=[
            dcc.Slider(
                id='my-slider',
                min=0,
                max=len(allDates)-1,
                value=len(allDates)-1,
                marks=datemarket
            ),
            dcc.Dropdown(
                id='DpercentDropdown',
                options=[{'label': percent, 'value': percent} for percent in percentD],
                value=percentD[0]),
            html.Div(id='slider-output-container')]),
        html.Div(children=[
            dcc.Loading(
                id="loading-1",
                type="default",
                children=dcc.Graph(
                    id='drought_heatmap',
                    figure=heatmap
                )
            ),
            dcc.Store(id="heatmap")])

    ]),

    html.Div(children=[
        dcc.Dropdown(
            id='counties-dropdown',
            options=[{'label': county, 'value': county} for county in allCounties],
            value=first_county)

    ]),

    html.Div(children=[
        dcc.Graph(
            id='county_table',
            figure=county_table
        ),
    ]),
    html.Div(children=[
        dcc.Dropdown(
            id='predDropdown',
            options=[{'label': percent, 'value': percent} for percent in percentD],
            value=percentD[0]),
        dcc.Graph(
            id='national',
            figure=tempGraphhh)
    ]),
])

server = app.server

@app.callback(
    dash.dependencies.Output('heatmap_selected_date', 'children'),
    [dash.dependencies.Input('my-slider', 'value')])
def update_heatmap_date(value):
    selectDateStr = allDates[value].strftime('%Y-%m-%d')
    return f'Heatmap on {selectDateStr}'

@cc.cached_callback(Output("heatmap", "data"),
                    [Input('my-slider', 'value'),
                     Input('DpercentDropdown', 'value'),
                     Trigger("my-slider", "value")])  # Trigger is like Input, but excluded from args
def query_data(value, value1):
    tempDate = allDates[value]
    tempPercent = value1
    return getHeatMap(df, tempDate, tempPercent)

@cc.callback(
    dash.dependencies.Output('drought_heatmap', 'figure'),
    [Input('heatmap', 'data'),
     dash.dependencies.Input('my-slider', 'value'),
     dash.dependencies.Input('DpercentDropdown', 'value')])
def update_heatmap_chart(heatmap, value, value1):

    return heatmap
    #tempDate = allDates[value]
    #tempPercent = value1
    #return getHeatMap(df, tempDate, tempPercent)


@app.callback(
    dash.dependencies.Output('county_table', 'figure'),
    [dash.dependencies.Input('counties-dropdown', 'value')])
def update_county_table(value):
    nd = df.query('county==@value')
    return getTable(hd, nd)

@app.callback(
    dash.dependencies.Output('national', 'figure'),
    [dash.dependencies.Input('predDropdown', 'value')])
def updatePred(value):
    return px.line(tempDf, x='ValidStart', y='hasDry_pre', color='bound', title=f'Prediction Training Graph')

cc.register(app)

if __name__ == '__main__':
    app.run_server(debug=False)

