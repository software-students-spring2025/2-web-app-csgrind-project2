from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

mongo = PyMongo()

def create_app():
    #load environment variables in memory
    load_dotenv()

    #access env variables
    ADMIN_URI = os.getenv("ADMIN_URI");
    USER_URI = os.getenv("USER_URI");   # for use when login auth is implemented

    #initialize flask app
    app = Flask(__name__)

    #set environment variable
    app.config["MONGO_URI"] = ADMIN_URI;

    #initialize mongo
    mongo.init_app(app)

    #register flask app with blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app