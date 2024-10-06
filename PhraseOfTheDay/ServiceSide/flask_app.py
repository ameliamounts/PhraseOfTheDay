import os
from flask import Flask
from phrase_generation import PhraseGenerator
from datetime import date

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    phrase_generator = PhraseGenerator()


    @app.route('/todaysPhrase')
    def getPhrase():
        return phrase_generator.get_todays_phrase(date.today()) # todo date needs to eventually be passed in from the client side
    
    return app