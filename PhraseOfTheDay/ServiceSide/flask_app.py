import os
from flask import Flask, request, jsonify
from phrase_generation import PhraseGenerator
from datetime import date

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    phrase_generator = PhraseGenerator()


    @app.route('/todaysPhrase')
    def getPhrase():
        headers = request.headers
        date = headers.get('Date')
        return jsonify(phrase_generator.get_todays_phrase(date))
    
    return app