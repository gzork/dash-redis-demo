import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import flask
import glob
import json
import redis
import time
import os
from tasks import hello

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('app', server=server)

if 'DYNO' in os.environ:
    if bool(os.getenv('DASH_PATH_ROUTING', 0)):
        app.config.requests_pathname_prefix = '/{}/'.format(
            os.environ['DASH_APP_NAME']
        )

r = redis.StrictRedis.from_url(os.environ['REDIS_URL'])

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'



# since layout is a function, it will be called on every page load
def layout():
    with open ('web.txt', 'a') as webfile:
        webfile.write('Web Process {}\n'.format(dt.now()))

    try:
        worker = open('worker.txt', 'r').read()
    except Exception as e:
        worker = 'Error reading worker.txt'
        print(e)

    try:
        web = open('web.txt', 'r').read()
    except Exception as e:
        worker = 'Error reading web.txt'
        print(e)

    return html.Div([
        html.H1('Redis INFO'),
        html.Div(children=html.Pre(str(r.info()))),
        html.Button(id='hello', type='submit', children='Run "Hello" task'),
        html.Div(id='target'),
        html.Pre(worker),
        html.Pre(web),
        html.Pre(json.dumps(glob.glob('*'), indent=2))
    ], className="container")

app.layout = layout

@app.callback(Output('target', 'children'), [], [], [Event('hello', 'click')])
def hello_callback():
    print 'DEBUG: callback hit'
    hello.delay()

app.css.append_css({
    'external_url': (
	'https://cdn.rawgit.com/plotly/dash-app-stylesheets/96e31642502632e86727652cf0ed65160a57497f/dash-hello-world.css'
    )
})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


if __name__ == '__main__':
    app.run_server()
