import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import json
import plotly.express as px
import numpy as np




df = pd.read_csv('covid_data_france_2.csv')
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
df=df.astype({'granularite':'string','maille_nom':'string'})
df.sort_values("date", inplace=True)

f=open('regions.geojson')
regions=json.load(f)

title_dic= { 'cas_confirmes':'confirmed cases',
             'deces':'death cases',
             'reanimation':'people in reanimation',
             'gueris':'people healed from the virus',
             'hospitalises':'people who are hospitalized'}

external_stylesheets = [

    {

        "href": "https://fonts.googleapis.com/css2?"

                "family=Lato:wght@400;700&display=swap",

        "rel": "stylesheet",

    },

]

app = dash.Dash("Covid",external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Img(src="https://img.icons8.com/color/96/000000/coronavirus--v2.png",className="center"),
                html.H1(children='Covid 19 Dashbord',className="header-title"),
                html.P(

                        children="Coronavirus Disease (COVID-19) Analytics in France",

                        className="header-description",

                    ),

            ],
            className="header"
        ),

       
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Metric", className="menu-title"),
                        dcc.Dropdown(id='dropdown', options=[
                            {'label': 'Confirmed Cases', 'value': 'cas_confirmes'},
                            {'label': 'deaths', 'value': 'deces'},
                            {'label': 'reanimation', 'value': 'reanimation'},
                            {'label': 'recoveries', 'value': 'gueris'},
                             {'label': 'hospitalized', 'value': 'hospitalises'}
                            ],
                        value = 'deces',
                        className="dropdown",
                        ),
                    ]
                ), 
                html.Div(
                    children=[
                        html.Div(children="Region", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[
                                {"label": region, "value": region}
                                for region in np.sort(df["maille_nom"].unique())
                            ],
                            value="France",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),               
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=df.date.min().date(),
                            max_date_allowed=df.date.max().date(),
                            start_date=df.date.min().date(),
                            end_date=df.date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ), 

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="graph-court", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
        
        html.Div(
            html.H1(children='Map for the mean values in France until now',className="header-description2"),
        ),
        html.Div(
            children=[
                 html.Div(
                    children=[
                        html.Div(children="Metric", className="menu-title"),
                        dcc.Dropdown(id='candidate', options=[
                            {'label': 'Confirmed Cases', 'value': 'cas_confirmes'},
                            {'label': 'deaths', 'value': 'deces'},
                            {'label': 'reanimation', 'value': 'reanimation'},
                            {'label': 'recoveries', 'value': 'gueris'},
                             {'label': 'hospitalized', 'value': 'hospitalises'}
                            ],
                        value = 'deces',
                        className="dropdown",
                        ),
                    ]
                ), 
            ],
         className="menu",
        ),

        html.Div(
            children=[
                html.Div(
                    children= dcc.Graph(id="map"),
                    className="card",
                ),
            ],
            className="wrapper",
        ),




    ]
)

@app.callback(
    Output('graph-court','figure'),
    [Input(component_id='dropdown', component_property='value'),
     Input("region-filter","value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date"),]
)
def update_figure(selected_value,region,start_date,end_date):
    
    mask = (
        (df.date <= end_date) 
        & (df.date >= start_date) 
        & (df['maille_nom']==region)
    )

    df_filtred=df.loc[mask,:]
    figure_chart={
            'data': [
                {
                    "x": df_filtred['date'],
                    "y": df_filtred[selected_value],
                    "type": "lines",
                    "name": selected_value,
                }
            ],
            "layout": {
                "title": "number of "+title_dic[selected_value]+" in "+region,
                "colorway": ["#17B897"]
            }
        }
    
    return figure_chart

@app.callback(
    Output('map','figure'),
    [Input('candidate','value'),]
)

def update_map(candidate):

    df_map = df[df['granularite']=='region']
    df2plot = df_map[['maille_nom',candidate]].groupby('maille_nom').mean().reset_index()

    fig = px.choropleth_mapbox(df2plot, geojson=regions, locations='maille_nom',
                           featureidkey="properties.nom",
                           color=candidate,
                           #color_continuous_scale="Viridis",
                           range_color=(0, df2plot[candidate].max()),
                           mapbox_style="carto-positron",
                           zoom=4, center = {"lat": 47.499998, "lon":  1.749997},
                           opacity=0.5,
                           labels={candidate:candidate}
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False)
