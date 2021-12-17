
# -*- coding: utf-8 -*-
import dash
from dash import html, dcc
import pandas as pd
import numpy as np
from decouple import config

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt


app = dash.Dash(__name__)
server = app.server
app.title = 'App uber'

# API keys and datasets
mapbox_access_token = config('MAPBOX_ACCESS_TOKEN')
df = pd.read_csv('uber_filtro.csv')

# Boostrap CSS.
# app.css.config.serve_locally = False
# app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})  # noqa: E501


# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("dash-logo-new.png")
                        ),
                        html.H2("DASH - UBER DATA APP"),
                        html.H6('Selecione Ano e/ou Mês:'),


                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="year",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in sorted(df['Year'].unique())
                                            ],
                                            multi=True,
                                            value=[2019,2018],
                                            placeholder="Selecione o ano",

                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="month",
                                            options=[
                                                {"label": n, "value": n}
                                                for n in range(1, 13)
                                            ],
                                            multi=True,
                                            value=[6,7,8],

                                            placeholder="Selecione o mês",
                                        )
                                    ],
                                ),
                            ],
                        ),
                        html.P(id="total-rides"),
                        html.P(id="total-rides-selection"),
                        html.P(id="date-value"),

                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph"),
                        html.Div(
                            className="text-padding",
                            children=[
                                "Select any of the bars on the histogram to section data by time."
                            ],
                        ),
                        dcc.Graph(id="histogram"),
                    ],
                ),
            ],
        )
    ]
)

# Update the total number of rides Tag


@app.callback(Output("total-rides", "children"),
              [Input("year", "value"),
               Input("month", "value")])

def update_total_rides(year, month):
    rides = lista(year, month)
    return f"Total de Viagens: {len(rides)}"

# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [Input("year", "value"), Input("month", "value")],
)
def update_histogram(year, month):
    rides = lista(year, month)
    count = rides['Hour'].value_counts()
    tuples = [tuple((x, y)) for x, y in count.items()]
    xVal = [x[0] for x in tuples]
    yVal = [y[1] for y in tuples]
    yVal = np.array(yVal)


    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]
    colorVal = np.array(colorVal)

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker={'color':xVal,'colorscale':'Viridis'}, hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal/2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )




def lista(year, month):

    if all(len(v) == 0 for v in [year, month]):
        rides = df
    elif year == None or len(year) == 0:
        rides = df[df['Month'].isin(month)]
    elif month == None or len(month) == 0:
        rides = df[df['Year'].isin(year)]
    else:
        mask = df[['Year', 'Month']].isin({'Year': year, 'Month': month}).all(axis=1)
        rides = df[mask]
    return rides


@app.callback(
    Output("map-graph", "figure"),
    [
        Input("year", "value"),
        Input("month", "value"),
    ],
)
def update_graph(year, month):
    zoom = 12.0
    latInitial = -3.74
    lonInitial = -38.49
    bearing = 0

    rides = lista(year, month)


    return go.Figure(
        data=[
            # Data for all rides based on date and time
            go.Scattermapbox(
                lat=rides['LatBegin'],
                lon=rides['LngBegin'],
                mode="markers",
                # text=rides.Hour,
                text="End: "+rides.BeginAddress+"<br>"+"Data: "+rides.pedido,
                hoverinfo="text",

                marker=dict(
                    showscale=True,
                    color=rides.Hour,
                    # color=np.append(np.insert([rides.Hour], 0, 0), 23),
                    opacity=0.5,
                    size=5,
                    colorscale=[
                        [0, "#F4EC15"],
                        [0.04167, "#DAF017"],
                        [0.0833, "#BBEC19"],
                        [0.125, "#9DE81B"],
                        [0.1667, "#80E41D"],
                        [0.2083, "#66E01F"],
                        [0.25, "#4CDC20"],
                        [0.292, "#34D822"],
                        [0.333, "#24D249"],
                        [0.375, "#25D042"],
                        [0.4167, "#26CC58"],
                        [0.4583, "#28C86D"],
                        [0.50, "#29C481"],
                        [0.54167, "#2AC093"],
                        [0.5833, "#2BBCA4"],
                        [1.0, "#613099"],
                    ],
                    colorbar=dict(
                        title="Hora do<br>Dia",
                        x=0.93,
                        xpad=0,
                        nticks=24,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                    ),
                ),
            ),

        ],
        layout=go.Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                style="dark",
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 12,
                                        "mapbox.center.lat": "-3.7491251",
                                        "mapbox.center.lon": "-38.4972" ,
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )


if __name__ == '__main__':
    app.run_server(debug=True)