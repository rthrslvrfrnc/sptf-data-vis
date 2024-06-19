import pandas as pd
import numpy as np
import dash
import pickle
from scipy.spatial import Delaunay
from shapely.geometry import MultiPoint
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output, State, callback_context
# from dash.dependencies import 
import plotly.express as px
from utils import get_custom_playlist
import time


# Load Data

spotify_top50_daily_wGenres = pd.read_csv('./data/universal_top_songs_final.csv',usecols=['spotify_id', 'track_name', 'artists', 'snapshot_date', 'genres', 'country_name'])
enao = pd.read_csv('./data/enao.csv', usecols=['color','top','left','size','genre'])

unique_countries = list(spotify_top50_daily_wGenres['country_name'].unique())
dropdown_options = [{'label': country_name, 'value': country_name} for country_name in unique_countries]

# Enao Alpha Shape

# Load x and y coordinates from the alpha shape polygon
with open('./data/convex_hull_enao', 'rb') as file:
  alpha_x, alpha_y = pickle.load(file)

size_max_default = 20

# Initialize Dash page
dash.register_page(__name__)


# App layout
layout = html.Div([    
    # Begining of first visualization section
    
    dcc.Markdown('''
                 ### Music Genre-Space
                 The graphic below displays the genre space for selected countries and time spans.
                 Each dot represents a genre, with its size corresponding to the number of songs in that genre.
                 The black line outlines the convex hull of Spotify's genre space distribution.
                 We've limited the number of countries selected to 3 due to resource constraints.

                 You can also add your personal Spotify playlist to analyze and compare your music genre space with the most popular genres from other cultures.
                 We’ve limited the playlist size to 100 tracks, also due to resource constraints. 
                 After clicking the 'add' button, your playlist will be added to the dropdown menu at the top right of the scatter plot.
                 
                 **Warning: If you opt to load your playlist, the loading time might be around 25–38 seconds.**                 
                 #### Add personal data (Optional):
                 '''),
    
    html.Div([
        # Options row
        html.Div([
            html.Label(children=html.B('Your playlist id:'), style={'display': 'block'}),
            dcc.Input(
                id='user-playlist-id',
                type='text',
                minLength=22,
                maxLength=22
            )
        ], style={'width': '24%', 'display': 'inline-block'}),
        html.Div([
            html.Label(children=html.B('Playlist Name:'), style={'display': 'block'}),
            dcc.Input(
                id='user-playlist-name',
                type='text',
                # minLength=22,
                maxLength=22
            ),
            html.Button('Add', id='submit-val', n_clicks=0)
        ], style={'width': '24%', 'display': 'inline-block'}),

        
        html.Div([
            # html.Label(children=html.B('Choose the countries:'), style={'display': 'block'}),
            # html.Button('Add', id='submit-val', n_clicks=0),
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    
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
            html.Label(children=html.B('Choose the countries (or custom playlists):'), style={'display': 'block'}),
            dcc.Dropdown(
                id='country-dropdown',
                options=dropdown_options,
                value=['Global', 'Brazil', 'Iceland'],
                multi=True,
                # clearable=False
                # disabled=False
                # placeholder='Select a country'
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    
    # Interactive visualizations from the first section
    html.Div([
        html.Div([
            dcc.Graph(id='enao-graph', style={'width': '100%', 'height': '600px',},config={'modeBarButtonsToRemove':['lasso2d']}, clickData={'points': [{'customdata': ['Global']}]})
        ]),
    ], style={'min-height': '100%', 'height': 'auto'}),
    html.Div([
        # Options row
        
        html.Div([
            html.Label(children=html.B('Scaling Factor:'), style={'marginRight': '10px'}),
            dcc.RadioItems(
                id='scaling-factor',
                options=[{'label': str(i+1), 'value': i+1} for i in range(4)],
                value=1,
                inline=True
            )
        ], style={'display': 'flex', 'alignItems': 'center'})

        
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Hr(),
    html.Div([
        html.Div([
            html.H2(id='table-genres-title'),
            dash_table.DataTable(
                sort_action="native",
                filter_action='native',
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    # 'maxWidth': '10px',
                },
                style_cell_conditional=[
                {
                    'if': {'column_id': 'track_name'},
                    'textAlign': 'left'
                },
                {
                    'if': {'column_id': 'artists'},
                    'textAlign': 'left'
                },
                {
                    'if': {'column_id': 'genres'},
                    'textAlign': 'left'
                },
                {
                    'if': {'column_id': 'country_name'},
                    'textAlign': 'left'
                },
            ],
                id='music-table-genre',
                columns=[{'name': 'Music', 'id': 'track_name'}, {'name': 'Artists', 'id': 'artists'}, {'name': 'Genres', 'id': 'genres'}, {'name': 'Country', 'id': 'country_name'}],
                data=[],
                page_size=10
            )
        ]),# style={'width': '39%', 'display': 'inline-block', 'height': '800px'}),
    ], style={'min-height': '100%', 'height': 'auto'}),
    dbc.Modal(
        [
            dbc.ModalHeader("Warning"),
            dbc.ModalBody("You must select at least one country."),
            dbc.ModalFooter(
                dbc.Button("Close", id="close", className="ml-auto")
            ),
        ],
        id="modal",
        is_open=False,
    ),
])

# Combined callback to update graph, dropdown options, and clearable property
@callback(
    Output('enao-graph', 'figure'),
    Output('country-dropdown', 'options'),
    Output('modal', 'is_open'),
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('country-dropdown', 'value'),
     Input('scaling-factor', 'value'),
     Input('submit-val', 'n_clicks'),
     Input('close', 'n_clicks')],
    [State('country-dropdown', 'options'),
     State('user-playlist-name', 'value'),
     State('user-playlist-id', 'value'),
     State('modal', 'is_open')]
)
def update_graph_and_dropdown(start_date, end_date, country_names, scaling_factor, n_clicks, close_clicks, curr_options, label, value, is_open):
    global spotify_top50_daily_wGenres
    global dropdown_options
    
    # Determine which input triggered the callback
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Modal control
    if triggered_id == 'close':
        return dash.no_update, dash.no_update, False
    
    if triggered_id == 'submit-val' and n_clicks > 0:
        labels = [item['label'] for item in curr_options]
        values = [item['value'] for item in curr_options]
        # print(f"c_o: {curr_options}")
        if label in labels or value in values:
            return dash.no_update, curr_options, is_open
        
        # start_time = time.time()
        table_data = get_custom_playlist(value, label, enao)
        # print("--- %s seconds ---" % (time.time() - start_time), flush=True)
        
        if table_data.empty:
            return dash.no_update, curr_options, is_open
        
        spotify_top50_daily_wGenres = pd.concat([spotify_top50_daily_wGenres, table_data], ignore_index=True)
        dropdown_options.append({'label': label, 'value': label})
        
        if len(country_names) < 3:
            curr_options.append({'label': label, 'value': label})
        
        return dash.no_update, curr_options, is_open
    
    
    # Validate number of selected options
    if len(country_names) < 1:
        return dash.no_update, dash.no_update, True
    
    # Update graph based on date range selection and country names
    
    
    drop_ops = dropdown_options if len(curr_options) == 3 and len(country_names) < 3 else curr_options
    # print(f"len_country_names: {len(country_names)}")
    if len(country_names) >= 3:
        drop_ops = [{"label": k, "value": k} for k in country_names[:3]]
        
    
    all_plots = []
    for country_name in country_names:
        filtered_df = filter_by_country_and_date(start_date=start_date, 
                                                 end_date=end_date, 
                                                 country_name=country_name, 
                                                 drop_duplicates=True, 
                                                 drop_subset='spotify_id', 
                                                 cols=['spotify_id', 'track_name', 'artists', 'genres'])

        filtered_data_gere_exp = filtered_df.assign(genres=filtered_df['genres'].str.split(', ')).explode('genres')
        genre_counts = filtered_data_gere_exp['genres'].value_counts().reset_index()
        genre_counts.columns = ['genre', 'song_count']

        plot_data_enao = pd.merge(enao, genre_counts, on='genre', how='inner')
        plot_data_enao['country'] = country_name
        all_plots.append(plot_data_enao)

    final_df = pd.concat(all_plots, ignore_index=True)
    
    fig = px.scatter(final_df, x='left', y='top', size='song_count', facet_col='country', facet_col_wrap=3,
                     size_max=size_max_default * scaling_factor, color='color', color_discrete_map="identity", 
                     hover_name='genre', custom_data=['country'], 
                     labels={"top": "y", "left": "x", "song_count": "Number of Songs"},
                     title=f'Genre-space in {", ".join(country_names)}')
    fig.update_traces(marker=dict(opacity=0.8))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.add_scatter(x=alpha_x, y=alpha_y, mode='lines', line=dict(color='black', width=0.5), showlegend=False, row='all', col='all')
    fig.update_layout(xaxis=dict(range=[-100, 1550]), yaxis=dict(range=[-1000, 23500]))
    fig.for_each_xaxis(lambda x: x.update({'title': ''}))
    fig.for_each_yaxis(lambda y: y.update({'title': ''}))

    fig.add_annotation(
        showarrow=False,
        xanchor='center',
        xref='paper', 
        x=0.5, 
        yref='paper',
        y=-0.1,
        text='← denser and atmospheric | spikier and bouncier →'
    )
    fig.add_annotation(
        showarrow=False,
        xanchor='center',
        xref='paper', 
        x=-0.03, 
        yanchor='middle',
        yref='paper',
        y=0.5,
        textangle=270,
        text='← organic | mechanical and electric →'
    )
    
    return fig, drop_ops, is_open



@callback(
    [Output('table-genres-title', 'children'),
     Output('music-table-genre', 'data')],
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('enao-graph', 'selectedData'),
     Input('enao-graph', 'clickData')]
)
def update_table(start_date, end_date,selectedData, clickData):
    
    # print(clickData, flush=True)
    # Custom Playlist
    # if selectedData:
    #     print(selectedData)
    #     print(len(selectedData['points']))
    
    
    
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'enao-graph' and ctx.triggered[0]['prop_id'].endswith('selectedData'):
        if selectedData:
            countries = []
            genres = set()
            for point in selectedData['points']:
                # print(point)
                genre = point['hovertext']
                genres.update(genre.split(', '))
                if point['customdata'][0] not in countries:
                    countries.append(point['customdata'][0])
            # print(countries)
            title = " Songs in " + ', '.join(countries)
            
            filtered_df = filter_by_country_and_date(start_date, 
                                             end_date, 
                                             countries,
                                             multy_country=True,
                                             drop_duplicates=True, 
                                             drop_subset='spotify_id', 
                                             cols=['spotify_id', 'track_name', 'artists', 'genres', 'country_name'])
            
            # Filter the DataFrame for rows containing any of these genres
            data_table = filtered_df[filtered_df['genres'].apply(lambda x: isinstance(x, str) and any(g in x.split(', ') for g in genres))]
            # Remove all rows with duplicate values in column 'A'
            data_table = data_table.drop_duplicates(subset=['track_name'], keep='first')
            # Select the desired columns
            data_table = data_table[['track_name', 'artists', 'genres', 'country_name']]

            # Create the title string from the selected genres
            title = 'Selected genres' + title
        else: 
            return dash.no_update, dash.no_update
    elif triggered_id == 'enao-graph' and ctx.triggered[0]['prop_id'].endswith('clickData'):
        country_name = clickData['points'][0]['customdata'][0]
        title = " Songs in " + country_name
        
        if 'hovertext' in clickData['points'][0].keys():
            filtered_df = filter_by_country_and_date(start_date, 
                                             end_date, 
                                             country_name,
                                             drop_duplicates=True, 
                                             drop_subset='spotify_id', 
                                             cols=['spotify_id', 'track_name', 'artists', 'genres', 'country_name'])
            genre = clickData['points'][0]['hovertext']
            data_table = filtered_df[filtered_df['genres'].apply(lambda x: isinstance(x, str) and genre in x.split(', '))]
            data_table = data_table[['track_name', 'artists', 'genres', 'country_name']]
            title = genre + title
        else:
            filtered_df = filter_by_country_and_date(start_date, 
                                             end_date, 
                                             country_name,
                                             drop_duplicates=True, 
                                             drop_subset='spotify_id', 
                                             cols=['spotify_id', 'track_name', 'artists', 'genres', 'country_name'])
            data_table = filtered_df[['track_name', 'artists', 'genres', 'country_name']]
    else:
        country_name = clickData['points'][0]['customdata'][0]
        title = " Songs in " + country_name
        filtered_df = filter_by_country_and_date(start_date, 
                                             end_date, 
                                             country_name,
                                             drop_duplicates=True, 
                                             drop_subset='spotify_id', 
                                             cols=['spotify_id', 'track_name', 'artists', 'genres', 'country_name'])
        data_table = filtered_df[['track_name', 'artists', 'genres', 'country_name']]
    


    
    return title, data_table.to_dict('records')


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

def filter_by_country_and_date(start_date, end_date, country_name, filter_date=True, drop_duplicates=False, drop_subset=None, cols=[],multy_country=False):
    
    if filter_date:
        if multy_country:
            date_country_filtered = spotify_top50_daily_wGenres[
                                    (
                                        (spotify_top50_daily_wGenres['snapshot_date'] >= start_date) &
                                        (spotify_top50_daily_wGenres['snapshot_date'] <= end_date) &
                                        (spotify_top50_daily_wGenres['country_name'].isin(country_name))
                                    ) |
                                    (
                                        (spotify_top50_daily_wGenres['snapshot_date'] == '') &
                                         (spotify_top50_daily_wGenres['country_name'].isin(country_name))
                                    )
                                ]
        else:  
            date_country_filtered = spotify_top50_daily_wGenres[
                                        (
                                            (spotify_top50_daily_wGenres['snapshot_date'] >= start_date) &
                                            (spotify_top50_daily_wGenres['snapshot_date'] <= end_date) &
                                            (spotify_top50_daily_wGenres['country_name'] == country_name)
                                        ) |
                                        (
                                            (spotify_top50_daily_wGenres['snapshot_date'] == '') &
                                            (spotify_top50_daily_wGenres['country_name'] == country_name)
                                        )
                                    ]
    else:
        date_country_filtered = spotify_top50_daily_wGenres[
                                              (spotify_top50_daily_wGenres['country_name'] == country_name)
                                              ]
    
    # Drop duplicates if specified
    if drop_duplicates:
        date_country_filtered = date_country_filtered.drop_duplicates(subset=drop_subset, keep='first')
    
    # Select specific columns if specified
    if cols:
        date_country_filtered = date_country_filtered[cols]
    
    return date_country_filtered
