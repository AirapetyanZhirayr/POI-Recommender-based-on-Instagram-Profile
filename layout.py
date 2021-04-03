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

btn_style = {'background': '#bdadf0',
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
             'text-transform': 'none',
             'justify-content': 'center',
             'text-align': 'center',
             'align-items': 'center',
             'display': 'flex'}


def create_card(id):
    return dbc.Card(
        [dbc.CardImg(src=None,
                     top=True,
                     style={'height': '20%'},
                     id='cardimg{}'.format(id)),
         dbc.CardBody(
             [html.P("empty yet", id='cardtext{}'.format(id))]
             , style={'height': '4rem'}),
         ], style={'height': '50%'})


def return_no_id_card(city, pic):
    return dbc.Card(
        [dbc.CardImg(src=pic,
                     top=True,
                     style={'height': '20%'}),
         dbc.CardBody(
             [html.P(city)]
             , style={'height': '4rem'}),
         ], style={'height': '50%'})


jumbotron = dbc.Jumbotron(
    [
        dbc.Container(
            [html.Div([
                html.H1("Point of Interest - Recommender", className="display-3", style={'font-variant': 'small-caps'}),
                html.P(
                    "From Instagram profile to new place.",
                    style={'font-variant': 'small-caps'},
                    className="lead"),
                html.Hr()
            ]
            )
            ],
            fluid=True,

        )
    ],
    fluid=True,
    style={'background-color': 'transparent',
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

card1 = create_card(1)
card2 = create_card(2)
card3 = create_card(3)
card4 = create_card(4)
card5 = create_card(5)

output = dbc.Spinner(html.Div(children=[
    dbc.Fade(children=[
        dbc.CardDeck([card1, card2, card3, card4, card5]),
        html.Hr(),
        html.Center(dbc.Button("Show user's photos",
                               id='example_btn',
                               style=btn_style))],
        id='fade',
        is_in=False,
        appear=False
    ),
    dbc.Fade(html.Div(children=[html.P('User not found :(',
                                       style={'text-align': 'center',
                                              'font-variant': 'small-caps',
                                              'font-size': '30px'},
                                       className="lead")]),
             is_in=False,
             id='fail')]

    , style={'padding': '50px'}
), color="info"
)

buffer = html.Div(children=[dbc.Fade(children=[None],
                                     is_in=False,
                                     id='ex_trigger')], id='example_pics',
                  style={'justify-content': 'center',
                         'text-align': 'center',
                         'align-items': 'center',
                         'display': 'flex'})

app.layout = html.Div(children=[jumbotron,
                                dbc.Row([input_form], style={'margin-top': '10px', 'justify-content': 'center'}),
                                output,
                                buffer],
                      style={'background': 'rgb(102,253,198)',
                             'background': 'linear-gradient(180deg, rgba(102,253,198,1) 0%, rgba(254,192,250,1) 47%, rgba(255,255,255,0.12975612608324583) 100%)'})


def test(name):
    return {
               "Tbilisi, Georgia": "https://scontent-arn2-1.cdninstagram.com/v/t51.2885-15/e35/23417349_816832125161746_1185414422554738688_n.jpg?tp=1&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_cat=110&_nc_ohc=KdnKH_YE-VsAX91xibD&edm=ABfd0MgAAAAA&ccb=7-4&oh=4673dde7492149f2216a0f32c42ec74c&oe=608E200A&_nc_sid=7bff83",
               "Sevana Lij": "https://scontent-arn2-1.cdninstagram.com/v/t51.2885-15/e35/23421705_340169433059961_8923086619511095296_n.jpg?tp=1&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_cat=109&_nc_ohc=oDb2aXJPjWQAX9N5BWD&edm=ABfd0MgAAAAA&ccb=7-4&oh=e614c5cf58d4ebc2afb9202d33c48207&oe=608E719D&_nc_sid=7bff83",
               "Blackberry-Yerevan": "https://scontent-arn2-1.cdninstagram.com/v/t51.2885-15/e35/23498311_394684067655133_2277167204795416576_n.jpg?tp=1&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_cat=101&_nc_ohc=VnJzht1Bvd4AX-RMpTP&edm=ABfd0MgAAAAA&ccb=7-4&oh=13655508e3ff3369de1f43f8d6350879&oe=608B2773&_nc_sid=7bff83"}, [
               'a', 'b', 'c', 'e', 'f']


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
    Output('ex_trigger', 'children'),
    Output('example_btn', 'style'),
    [Input('start_btn', 'n_clicks')],
    [State('fade', 'is_in'),
     State('input-acc', 'value')]
)
def get_preds(click, is_in, acc_name):
    if not click:
        raise PreventUpdate
    if click:
        time.sleep(1)
    examples, answers = predict_user(acc_name)
    # examples, answers = test(acc_name)

    if not answers:
        return False, True, None, None, None, None, None, None, None, None, None, None, None, None

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

    city_list_example = list(examples.keys())
    pic_list_example = list(examples.values())

    if city_list_example:
        ex1 = return_no_id_card(city_list_example[0], pic_list_example[0])
        btn_style_dict = btn_style
    else:
        ex1 = None
        btn_style_dict = {'display': 'none'}
    if len(city_list_example) >= 2:
        ex2 = return_no_id_card(city_list_example[1], pic_list_example[1])
    else:
        ex2 = None
    if len(city_list_example) >= 3:
        ex3 = return_no_id_card(city_list_example[2], pic_list_example[2])
    else:
        ex3 = None
    if len(city_list_example) >= 4:
        ex4 = return_no_id_card(city_list_example[3], pic_list_example[3])
    else:
        ex4 = None
    if len(city_list_example) >= 5:
        ex5 = return_no_id_card(city_list_example[4], pic_list_example[4])
    else:
        ex5 = None
    pics = dbc.CardDeck([ex1, ex2, ex3, ex4, ex5])

    # example_block = dbc.Fade(children=[dbc.CardDeck([ex1, ex2, ex3, ex4, ex5])],
    #                          is_in=False,
    #                          id='ex_trigger')

    return not is_in, False, city1, city2, city3, city4, city5, pic1, pic2, pic3, pic4, pic5, pics, btn_style_dict


@app.callback(
    Output('ex_trigger', 'is_in'),
    [Input('example_btn', 'n_clicks')],
    [State("ex_trigger", "is_in")]
)
def show_user_pics(click, isin):
    if not click:
        raise PreventUpdate
    return not isin


if __name__ == '__main__':
    app.run_server(debug=True)