from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Creating your flaskapp instance
app = Flask(__name__, instance_relative_config=True)

# Try to load from config file, but use a default if not found
try:
    app.config.from_pyfile('config.py')
except FileNotFoundError:
    app.config['SECRET_KEY'] = 'my_secret_key'
    print("Warning: config.py not found, using default secret key")

# Configuring the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating a SQLAlchemy database instance
db = SQLAlchemy(app)
app.app_context().push()

from flaskapp import routes