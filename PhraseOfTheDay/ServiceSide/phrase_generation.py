from datetime import date
from google import genai
import json
import os
import queue
import typing_extensions as typing

from phrases_db_interface import db_interface
from phrase import Phrase

class PhraseType(typing.TypedDict):
    phrase: str
    description: str
    example: str

class PhraseGenerator:
    def __init__(self):
        self.database = db_interface()
        self.m_phrases_queue = queue.Queue()
        self.m_todays_phrase = None
        self.m_last_three_phrases = []
        if self.m_phrases_queue.empty():
            self._fill_queue()
    
    def _fill_queue(self, retries=0):
        # generate 20 phrases
        used_phrases_str = self.database.get_used_phrases_string()
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        if not used_phrases_str == "":
            prompt = "Collect quirky and largely \
                    unknown English turns of phrases between 2 and 10 words long used \
                    within the last 200 years. Return 20 \
                    phrases, provide a descrption, and use the phrase properly in a sentance \
                    Do not use phrases from the following list: {used_phrases}"
            prompt = prompt.format(used_phrases = used_phrases_str)
        else:
            prompt = "Collect quirky and largely \
                    unknown English turns of phrases between 2 and 10 words long used \
                    within the last 200 years. Return 20 \
                    phrases, provide a descrption, and use the phrase properly in a sentance"
        response = client.models.generate_content(model="gemini-2.0-flash", 
                                                  contents=prompt, 
                                                  config={
                                                      'response_mime_type': 'application/json',
                                                      'response_schema': list[PhraseType],
                                                      })
        try:
            response_json = json.loads(response.text + "\n")
            for entry in response_json:
                if 'phrase' not in entry or 'description' not in entry or 'example' not in entry:
                        continue
                if not self.database.phrase_exists(entry['phrase']):
                    phrase_object = Phrase(entry['phrase'], entry['description'], entry['example'])
                    self.m_phrases_queue.put(phrase_object)
        except ValueError as e:
            print("Response not in a valid json format:" + response.text)

        if self.m_phrases_queue.empty():
            retries += 1
            if retries < 15:
                print("queue empty, retrying")
                self._fill_queue(retries)
            else:
                print("Exceeded retry limit, no valid phrases were generated.")
        return
    
    def pull_phrase_from_queue(self, date):
        if self.m_phrases_queue.empty():
            self._fill_queue()
        # we know it's not empty now
        todays_phrase = self.m_phrases_queue.get()
        while (self.database.phrase_exists(todays_phrase.get_phrase())):
            while self.m_phrases_queue.empty():
                self._fill_queue()
            todays_phrase = self.m_phrases_queue.get()

        todays_phrase.set_date(date)
        self.database.insert_phrase(todays_phrase.get_phrase(), todays_phrase.get_description(), todays_phrase.get_example(), date)
        self.add_to_recents(todays_phrase)
        return todays_phrase
    
    def in_recent_phrases(self, date):
        for phrase in self.m_last_three_phrases:
            if phrase.get_date() == date:
                return phrase
        return None
    
    def add_to_recents(self, todays_phrase):
        if len(self.m_last_three_phrases) < 3:
            self.m_last_three_phrases.append(todays_phrase)
        oldest_index = 0
        for i in range(len(self.m_last_three_phrases)):
            if  self.m_last_three_phrases[i].get_date() < self.m_last_three_phrases[oldest_index].get_date():
                oldest_index = i
        self.m_last_three_phrases[oldest_index] = todays_phrase

    def get_todays_phrase(self, date):
        todays_phrase = self.in_recent_phrases(date)
        if todays_phrase:
            return todays_phrase.to_dict()
        todays_phrase = self.database.get_phrase_for_date(date)
        if todays_phrase:
            self.add_to_recents(todays_phrase)
            return todays_phrase.to_dict()
        return self.pull_phrase_from_queue(date).to_dict()
