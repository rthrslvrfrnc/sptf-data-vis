import pandas as pd
import numpy as np
import dash
import pickle
from scipy.spatial import Delaunay
from shapely.geometry import MultiPoint
from dash import dcc, html, dash_table, callback, Input, Output
# from dash.dependencies import 
import plotly.express as px
import plotly.graph_objects as go

# Load Data

spotify_top50_daily_wGenres = pd.read_csv('./data/universal_top_songs_final.csv',usecols=[ 'country_name', 'snapshot_date', 'country_region',
       'danceability', 'energy', 'loudness', 'speechiness',
       'acousticness', 'instrumentalness', 'liveness', 'valence'])

# Enao Alpha Shape


# Initialize Dash page
dash.register_page(__name__)


# App layout
layout = html.Div([
    html.Div([
        dcc.Markdown('''
                     ### Music Features Overview
                        The scatter plot on the left is the average value of x and y features on the selected date for each country,
                        they are collored based on its continent.
                        You can change the x and y axis to any of the following track features listed below.
                        
                        On the right you can see the time series of the selected x and y features.
                        
                        **Audio Feature list:**
                        
                        - **acousticness**: A confidence measure from 0.0 to 1.0 of whether the track is acoustic.
                        - **danceability**: Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity.
                        - **energy**: Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. 
                        - **liveness**: Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live.
                        - **speechiness**: Speechiness detects the presence of spoken words in a track.
                        - **instrumentalness**: Predicts whether a track contains no vocals.  The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content.
                        - **valence**: A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.
                        
                     '''),
        # - **loudness**: The overall loudness of a track in decibels (dB). Values typically range between -60 and 0 db.
        html.Hr(),
        html.Div([
            html.Label(children=html.B('x axis:'), style={'display': 'block'}),
            dcc.Dropdown(
                sorted(['danceability', 'energy', 'speechiness',
                'acousticness', 'instrumentalness', 'liveness', 'valence']),
                'danceability',
                id='crossfilter-xaxis-column',
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='crossfilter-xaxis-type',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            html.Label(children=html.B('y axis:'), style={'display': 'block'}),
            dcc.Dropdown(
                ['danceability', 'energy', 'speechiness',
                'acousticness', 'instrumentalness', 'liveness', 'valence'],
                'liveness',
                id='crossfilter-yaxis-column'
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='crossfilter-yaxis-type',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            ),
            
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            clickData={'points': [{'hovertext': 'Japan'}]}
        ),
        html.Label(children=html.B('Choose a date:'), style={'display': 'block'}),
        html.Div(dcc.DatePickerSingle(
                id='crossfilter-year--slider',
                min_date_allowed=spotify_top50_daily_wGenres['snapshot_date'].min(),
                max_date_allowed=spotify_top50_daily_wGenres['snapshot_date'].max(),
                initial_visible_month=spotify_top50_daily_wGenres['snapshot_date'].min(),
                date=spotify_top50_daily_wGenres['snapshot_date'].min()
            ), style={'width': '100%', 'padding': '20px 0'})
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
        html.Div([
            html.Label(children=html.B('Window Size:'), style={'marginRight': '10px'}),
            dcc.RadioItems(
                id='sliding-window',
                options=[{'label': str(i+1), 'value': i+1} for i in range(5 ) if not i%2],
                value=1,
                inline=True
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'padding': '20px 0'})
    ], style={'display': 'inline-block', 'width': '49%'})
])

@callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    Input('crossfilter-xaxis-column', 'value'),
    Input('crossfilter-yaxis-column', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('crossfilter-yaxis-type', 'value'),
    Input('crossfilter-year--slider', 'date'))
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
  
  grouped_d = spotify_top50_daily_wGenres.groupby([ 'country_name', 'snapshot_date', 'country_region']).mean().reset_index()
  grouped_d = grouped_d[grouped_d['snapshot_date'] == year_value]
  # filtered_data = grouped_d[(grouped_d['snapshot_date'] >= start_date) & (grouped_d['snapshot_date'] <= end_date)]
  
  fig = px.scatter(grouped_d, x=xaxis_column_name, y=yaxis_column_name, color='country_region',
                   hover_data={
                      xaxis_column_name: ':.3r',
                      yaxis_column_name: ':.3r',
                    },
                    
                    labels={                        
                        "country_region": "Country Region",
                    },
                    # labels={                        
                    #     # "country": False,
                    #     "country_name": "Country Name",
                    #     "appearance_percentage": "Appearance Percentage"
                    # },
                #  title='Mean Danceability vs. Energy by Country',
                 hover_name='country_name')
  
  
  
    # dff = spotify_top50_daily_wGenres[spotify_top50_daily_wGenres['Year'] == year_value]

    # fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
    #         y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
    #         hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name']
    #         )

  # fig.update_traces(customdata=grouped_d['grouped_d[] == yaxis_column_name']['Country Name'])

  fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')

  fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log')

  fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

  return fig


def create_time_series(dff, axis_type, title, column_name):

    fig = px.scatter(dff, x='snapshot_date', y=column_name,
                     hover_data={
                      column_name: ':.3r',
                    },)

    fig.update_traces(mode='lines')

    fig.update_xaxes(showgrid=False)

    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')

    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)

    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

    return fig


@callback(
    Output('x-time-series', 'figure'),
    Input('crossfilter-indicator-scatter', 'clickData'),
    Input('crossfilter-xaxis-column', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('sliding-window', 'value'))
def update_x_timeseries(hoverData, xaxis_column_name, axis_type, window_size):
    # print(str(hoverData), flush=True)
    country_name = hoverData['points'][0]['hovertext']
    dff = spotify_top50_daily_wGenres[spotify_top50_daily_wGenres['country_name'] == country_name]
    dff = dff.groupby([ 'country_name', 'snapshot_date', 'country_region']).mean().reset_index()
    dff['snapshot_date'] = pd.to_datetime(dff['snapshot_date'])
    
    dff = dff[[xaxis_column_name, 'snapshot_date']]
    
    dff = dff.sort_values(by='snapshot_date')
    dff[xaxis_column_name] = dff[xaxis_column_name].rolling(window=window_size).mean()
    # print(dff.head(), flush=True)
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title, xaxis_column_name)


@callback(
    Output('y-time-series', 'figure'),
    Input('crossfilter-indicator-scatter', 'clickData'),
    Input('crossfilter-yaxis-column', 'value'),
    Input('crossfilter-yaxis-type', 'value'),
    Input('sliding-window', 'value'))
def update_y_timeseries(hoverData, yaxis_column_name, axis_type, window_size):
    # print(str(hoverData), flush=True)
    country_name = hoverData['points'][0]['hovertext']
    dff = spotify_top50_daily_wGenres[spotify_top50_daily_wGenres['country_name'] == country_name]
    dff = dff.groupby([ 'country_name', 'snapshot_date', 'country_region']).mean().reset_index()
    dff['snapshot_date'] = pd.to_datetime(dff['snapshot_date'])
    
    dff = dff[[yaxis_column_name, 'snapshot_date']]
    
    dff = dff.sort_values(by='snapshot_date')
    dff[yaxis_column_name] = dff[yaxis_column_name].rolling(window=window_size).mean()
    return create_time_series(dff, axis_type, yaxis_column_name, yaxis_column_name)
