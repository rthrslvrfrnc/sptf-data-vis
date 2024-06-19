import dash
import pickle
from dash import dcc, html

# Load Enao Fig
with open('./data/enaofig', 'rb') as file:
  enaofig = pickle.load(file)

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('Data and Visualizations Overview.'),
    
    dcc.Markdown('''
                 
                 '''),
    
    html.Div([
      dcc.Markdown('''
                   
                   On this page, you'll learn more about the goals and data used in this visualization project. 
                   If you want to jump straight to the visualizations and explore on your own, use the menu on the left to select what interests you. :)
                   
                   ## Data Domain and Sources
                   
                   
                   
                    As you can see in the menu header, we've chosen the music domain for this project!

                    What is music? According to [Jean Molino](https://en.wikipedia.org/wiki/Jean_Molino),  
                    music is a total social fact whose definitions vary according to era and culture. 
                    Moreover, the boundary between music and noise is always culturally defined, 
                    and there is rarely consensus on where this boundary lies, even within a single society.

                    Music has been described as a universal cultural element that transcends borders and connects us as humans. 
                    Like many other media, music consumption today is primarily stream-based, 
                    providing us with easy access to data that can help understand many complex discussions on the subject.

                    Spotify, one of the biggest music streaming services in the world, 
                    has an API for developers that allows access to a wide range of data about users, 
                    artists, albums, and tracks. Spotify also maintains Top 50 songs playlists in over 70 different countries, 
                    as well as a global one. Tracking these playlists allows us to build visualizations that can help understand 
                    the impact of culture on music consumption, identify exceptions, 
                    and observe events that disrupt typical consumption patterns.
                    
                    We used [Top Spotify Songs in 73 Countries (Daily Updated)](https://www.kaggle.com/datasets/asaniczka/top-spotify-songs-in-73-countries-daily-updated), 
                    as our main dataset. The Mantainer updates Spotify's top 50 playlist charts for 72 countries as well as the global chart daily since October 18, 2023. 
                    It contains a multitude of features for each track, these features range from popularity and audio mesures as well as 
                    market availibility, daily and weekly movement, amongst others.
                    
                    We foucussed on the features that would better suit our proposal as well as time and resources constrains. 
                    We really wanted to explore the **cultural** impact in music consumption across different countries, ant to do so 
                    we judge important to also have data reggarding the music genre of each track. Since the information isnt available in 
                    the dataset, we used Spotify's Developers API to complement the database.
                   

                   
                   
                   
                   ''')
      
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    
    
    html.Div([
        html.Div([
            dcc.Markdown('''
                ## Musical Genre-space of Spotify Top 50 Songs
                One of our goals is to visualize the music genre-space of the top 50 songs in each country!
                
                ### Enao overview:
                
                
                
                To achieve this, we've scraped data from [Every Noise at Once](https://everynoise.com/), an ongoing attempt at an 
                algorithmically-generated, readability-adjusted scatter-plot of the musical genre-space. 
                This plot is based on data tracked and analyzed for 6,291 genre-shaped distinctions by Spotify, carried out by 
                [glenn mcdonald](https://furia.com/), a former Data Scientist at the company. 
                The calibration is fuzzy, but in general, down is more organic, up is more mechanical and electric; 
                left is denser and more atmospheric, and right is spikier and bouncier. 
                In addition to the X and Y axes, McDonald used the color-space to represent other analytical dimensions from the 
                underlying music space by mapping the acoustic metrics of energy, dynamic variation, 
                and instrumentalness into the red, green, and blue channels respectively.

                On the right, you can see a plot of the scraped data. 
                Each dot represents a genre, and the black line outlines the convex shape of Spotify's genre-space distribution.
                
                
                **That's it for the introductions; we hope you enjoy our work! =]**
                
            '''),
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),

        html.Div([
            html.Div([
                dcc.Graph(id='ENAO-genre-space',
                    
                     figure=enaofig)    
            ], style={'width':'400px','marginLeft': 'auto', 'marginRight': 'auto'})
            
        ], style={'width': '49%', 'display': 'inline-block', 'height': '400px'}),
    ], style={'display': 'flex', 'flexDirection': 'row'}),
    
    
    # html.Div('This is our Home page content.'),
])