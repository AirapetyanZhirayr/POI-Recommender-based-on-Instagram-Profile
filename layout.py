# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import time
import os
from launcher import predict_user

# from cards import card1, card2, card3, card4, card5


import dash_bootstrap_components as dbc
import dash_html_components as html

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'POI Recommender'

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

jumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [html.Div([
                html.H1("Point of Interest - Recommender", className="display-3", style={'font-variant': 'small-caps'}),
                html.P(
                    "From Instagram profile to new place.",
                    style={'font-variant': 'small-caps'},

                    className="lead",

                ),
                html.Hr()
                # html.P(
                #     "You will need to embed a fluid container in "
                #     "the jumbotron.",
                #     className="lead",style ={'font-size':'xx-small'}
            ])],
            fluid=True,

        )
    ],
    fluid=True, style={'background-color': 'transparent',
                       'padding-top': '1%',
                       'padding-bottom': '0%'})

input_form = dbc.InputGroup(
    [
        dbc.Input(id="input-acc",
                  placeholder="Input your account name...",
                  style={'padding': '5px',
                         'font-size': '16px',
                         'border-width': '1px',
                         'border-color': '#CCCCCC',
                         'background-color': '#ffffff',
                         'color': '#000000',
                         'border-style': 'solid',
                         'border-radius': '29px',
                         # 'box-shadow': '0px 0px 5px rgba(66,66,66,.75)',
                         # 'font-size': '12px',
                         'padding': '10px 20px 10px 20px',
                         'text-decoration': 'none',
                         'border': 'none',
                         'outline': 'none',
                         'font-family': 'Tahoma, Geneva, sans-serif',
                         'font-size': '14px',
                         'letter-spacing': '1px',
                         'word-spacing': '1.6px',
                         # 'color': '#ffffff',
                         'font-weigh': 'normal',
                         'text-decoration': 'none',
                         'font-style': 'normal',
                         'font-variant': 'small-caps',
                         'text-transform': 'none'
                         }),
        dbc.InputGroupAddon(
            dbc.Button("Go!", id='start_btn', active=True,
                       style={'background': '#bdadf0',
                              # 'background-image': '-webkit-linear-gradient(top, #bdadf0, #2c97b8)',
                              # 'background-image': '-moz-linear-gradient(top, #bdadf0, #2c97b8)',
                              # 'background-image': '-ms-linear-gradient(top, #bdadf0, #2c97b8)',
                              # 'background-image': '-o-linear-gradient(top, #bdadf0, #2c97b8)',
                              # 'background-image': 'linear-gradient(to bottom, #bdadf0, #2c97b8)',
                              '-webkit-border-radius': '60',
                              '-moz-border-radius': '60',
                              'border-radius': '60px',
                              # 'color': '#ffffff',
                              'font-size': '12px',
                              # 'padding': '10px 20px 10px 20px',
                              'text-decoration': 'none',
                              'border': 'none',
                              'outline': 'none',
                              'font-family': 'Tahoma, Geneva, sans-serif',
                              # 'font-size': '14px',
                              'letter-spacing': '1px',
                              'word-spacing': '1.6px',
                              'color': '#ffffff',
                              'font-weigh': 'normal',
                              'text-decoration': 'none',
                              'font-style': 'normal',
                              'font-variant': 'small-caps',
                              'text-transform': 'none'}),
            addon_type="prepend"
        )
    ], style={'width': '50%',
              'display': 'flex',
              'justify-content': 'center',
              'padding-top': '45px'}
)

card1 = dbc.Card(
    [
        dbc.CardImg(src=None,
                    top=True,
                    style={'height': '20%'},
                    id='cardimg1'),
        dbc.CardBody(
            [
                html.P("empty yet", id='cardtext1')
            ]
            , style={'height': '4rem'}),
    ]
    , style={'height': '50%'})

card2 = dbc.Card(
    [
        dbc.CardImg(src=None,
                    top=True,
                    style={'height': '20%'},
                    id='cardimg2'),
        dbc.CardBody(
            [
                html.P("empty yet", id='cardtext2')
            ]
            , style={'height': '4rem'}),
    ]
    , style={'height': '50%'})

card3 = dbc.Card(
    [
        dbc.CardImg(src=None,
                    top=True,
                    style={'height': '20%'},
                    id='cardimg3'),
        dbc.CardBody(
            [
                html.P("empty yet", id='cardtext3')
            ]
            , style={'height': '4rem'}),
    ]
    , style={'height': '50%'})

card4 = dbc.Card(
    [
        dbc.CardImg(src=None,
                    top=True,
                    style={'height': '20%'},
                    id='cardimg4'),
        dbc.CardBody(
            [
                html.P("empty yet", id='cardtext4')
            ]
            , style={'height': '4rem'}),
    ]
    , style={'height': '50%'})

card5 = dbc.Card(
    [
        dbc.CardImg(src=None,
                    top=True,
                    style={'height': '20%'},
                    id='cardimg5'),
        dbc.CardBody(
            [
                html.P("empty yet", id='cardtext5')
            ]
            , style={'height': '4rem'}),
    ]
    , style={'height': '50%'})

output = dbc.Spinner(html.Div(children=[
    dbc.Fade(
        dbc.CardDeck([card1, card2, card3, card4, card5]),
        id='fade',
        is_in=False,
        appear=False
    ),
    dbc.Fade(html.Div(children=[html.P('Sorry, no recommendation for you :(',
                                       style={'text-align': 'center',
                                              'font-variant': 'small-caps',
                                              'font-size': '30px'},
                                       className="lead")]),
             is_in=False,
             id='fail')]

    , style={'padding': '50px'}
), color="info"
)

app.layout = html.Div(children=[jumbotron,
                                dbc.Row([input_form], style={'margin-top': '10px', 'justify-content': 'center'}),
                                output],
                      style={'background': 'rgb(102,253,198)',
                             'background': 'linear-gradient(180deg, rgba(102,253,198,1) 0%, rgba(254,192,250,1) 47%, rgba(255,255,255,0.12975612608324583) 100%)'})


def get_photo_from_city(city):
    cities_photos = pd.read_csv('data/pics.csv')
    return cities_photos.loc[cities_photos.location == city]['source']


@app.callback(
    Output('fade', 'is_in'),
    Output('fail', 'is_in'),
    Output('cardtext1', 'children'),
    Output('cardtext2', 'children'),
    Output('cardtext3', 'children'),
    Output('cardtext4', 'children'),
    Output('cardtext5', 'children'),
    Output('cardimg1', 'src'),
    Output('cardimg2', 'src'),
    Output('cardimg3', 'src'),
    Output('cardimg4', 'src'),
    Output('cardimg5', 'src'),
    [Input('start_btn', 'n_clicks')],
    [State('fade', 'is_in'),
     State('input-acc', 'value')]
)
def get_preds(click, is_in, acc_name):
    if not click:
        raise PreventUpdate
    if click:
        time.sleep(1)
    answers = predict_user(acc_name)
    if not answers:
        return False, True, None, None, None, None, None, None, None, None, None, None

    city1 = answers[0]
    city2 = answers[1]
    city3 = answers[2]
    city4 = answers[3]
    city5 = answers[4]

    pic1 = get_photo_from_city(city1)
    pic2 = get_photo_from_city(city2)
    pic3 = get_photo_from_city(city3)
    pic4 = get_photo_from_city(city4)
    pic5 = get_photo_from_city(city5)

    return not is_in, False, city1, city2, city3, city4, city5, pic1, pic2, pic3, pic4, pic5


if __name__ == '__main__':
    app.run_server(debug=True)