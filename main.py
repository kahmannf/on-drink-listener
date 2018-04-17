from flask import Flask, request, render_template, url_for, session, redirect, flash
from sys import argv
from configuration import get_config
from data import Data
from controller import Controller

from blprt_view import view_blueprint

app = Flask(__name__)

server_config = get_config()

controller = Controller()

app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY= server_config.get('secret_key', 'dev_key')
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.register_blueprint(view_blueprint)

app.config['UPLOAD_FOLDER'] = '/static/images/'

def main():
    app.run(host=server_config['flask_host_name'],port=server_config['flask_port'])

if __name__ == '__main__':
    main()