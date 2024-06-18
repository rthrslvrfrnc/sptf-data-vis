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

spotify_top50_daily_wGenres = pd.read_csv('./data/universal_top_songs_final.csv',usecols=['artists', 'snapshot_date', 'country_name', 'country'])
spotify_top50_daily_wGenres['primary_artist'] = spotify_top50_daily_wGenres['artists'].str.split(', ').str[0]


# Initialize Dash page
dash.register_page(__name__)


# App layout
layout = html.Div([

    # Begining of first visualization section
    
    dcc.Markdown('''
                 ### Most Popular Artists
                 The map below shows the most popular artists in each country for the selected time span.
                 The colors represent the percentage of appearances of the top artist in the top 50 chart.
                 
                 '''),
    html.Hr(),
    html.Div([
        # Options row
        html.Div([
            html.Label(children=html.B('Choose a time span:'), style={'display': 'block'}),
            dcc.DatePickerRange(
                id='date-range-picker',
                start_date=spotify_top50_daily_wGenres['snapshot_date'].min(),
                end_date=spotify_top50_daily_wGenres['snapshot_date'].max(),
                display_format='YYYY-MM-DD'
            )
        ], style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    # Interactive visualizations from the first section
    html.Div([
        html.Div([
            dcc.Graph(id='world-map', style={'width': '100%', 'height': '100%'})
        ]),#, style={'width': '59%', 'display': 'inline-block', 'padding': '0 20'}),

        
    ]),

    
])

# Callback to update graph based on date range selection
@callback(
    Output('world-map', 'figure'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')]
)
def update_graph(start_date, end_date):
    
    

    
  filtered_df = filter_by_date(start_date, 
                              end_date,  
                              drop_duplicates=False)
  filtered_df = filtered_df[filtered_df['country_name'] != 'Global']
  artist_appearances = filtered_df.groupby(['country', 'primary_artist']).size().reset_index(name='chart_placements')
  # Calculate the total number of chart placements for each country
  total_placements = filtered_df.groupby('country')['snapshot_date'].nunique() * 50
  total_placements = total_placements.reset_index(name='total_placements')
  
  # Merge to get total placements for each country
  artist_appearances = artist_appearances.merge(total_placements, on='country')
  
  # Calculate the appearance percentage
  artist_appearances['appearance_percentage'] = (artist_appearances['chart_placements'] / artist_appearances['total_placements']) * 100
  
  # Find the top artist for each country based on the appearance percentage
  top_artists = artist_appearances.loc[artist_appearances.groupby('country')['appearance_percentage'].idxmax()]
  
  # Merge with filtered_df to get country_name
  country_names = filtered_df[['country', 'country_name']].drop_duplicates()
  top_artists = top_artists.merge(country_names, on='country', how='left')
  
  # Display the result
  # print(top_artists[['country', 'country_name', 'primary_artist', 'chart_placements', 'total_placements', 'appearance_percentage']], flush=True)

  

  fig = px.choropleth(top_artists, locations='country', 
                    locationmode="ISO-3",
                    color='appearance_percentage',
                    hover_name='primary_artist',
                    hover_data={
                      'country': False,
                      'country_name': True,
                      'appearance_percentage': ':.3r'
                    },
                    labels={                        
                        # "country": False,
                        "country_name": "Country Name",
                        "appearance_percentage": "Appearance Percentage"
                    },
                    projection='equirectangular',
                    template='plotly_dark'
                    # color_discrete_map={'High':'red',
                    #                     'Moderate':'Yellow',
                    #                     'Low':'Green'}
                    # scope="south america"
                    
                   )
  
  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, legend_title="Apperence percentage:",)
  
  fig.add_scattergeo(
    
    locations=top_artists['country'],
    locationmode='ISO-3',
    text=top_artists['primary_artist'],
    mode='text',
    textfont={'color': 'White'},
    # hovertemplate=None
    hoverinfo='none'
  )
  
  # fig.update_traces(textposition='inside')
  fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
  # fig.update_traces(textposition='inside', textfont_size=14)
  
  return fig


# @callback(
#     [Output('table-title', 'children'),
#      Output('music-table', 'data')],
#     [Input('date-range-picker', 'start_date'),
#      Input('date-range-picker', 'end_date'),
#      Input('country-dropdown', 'value'),
#      Input('enao-graph', 'clickData')]
# )
# def update_table(start_date, end_date, country_name, clickData):
    
#     filtered_df = filter_by_country_and_date(start_date, 
#                                              end_date, 
#                                              country_name, 
#                                              drop_duplicates=True, 
#                                              drop_subset='spotify_id', 
#                                              cols=['spotify_id', 'track_name', 'artists', 'genres'])
    
#     # Split genres in df_songs into individual rows
#     filtered_data_gere_exp = filtered_df.assign(genres=filtered_df['genres'].str.split(', ')).explode('genres')

#     title = " Songs in " + country_name
#     if clickData:
#         genre = clickData['points'][0]['hovertext']
#         data_table = filtered_data_gere_exp[(filtered_data_gere_exp['genres'] == genre)]
#         data_table = data_table[['track_name', 'artists']]
#         title = genre + title
#     else:
#         data_table = filtered_df[['track_name', 'artists']]

    
#     return title, data_table.to_dict('records')


# Auxiliar Functions

def find_factors(n_country):
    '''
        find the x and y plot ratio
    '''
    f1 = 0
    f2 = n_country
    while f1+1 <= f2:
        f1 += 1
        if n_country % f1 == 0:
            f2 = n_country // f1
    
    return f1, f2

def filter_by_date(start_date, end_date, drop_duplicates=False, drop_subset=None, cols=[]):
    
    date_country_filtered = spotify_top50_daily_wGenres[(spotify_top50_daily_wGenres['snapshot_date'] >= start_date) &
                                              (spotify_top50_daily_wGenres['snapshot_date'] <= end_date)
                                              ]
    
    # Drop duplicates if specified
    if drop_duplicates:
        date_country_filtered = date_country_filtered.drop_duplicates(subset=drop_subset, keep='first')
    
    # Select specific columns if specified
    if cols:
        date_country_filtered = date_country_filtered[cols]
    
    return date_country_filtered
