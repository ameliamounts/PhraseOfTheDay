import queue
from datetime import date
import google.generativeai as genai
import typing_extensions as typing
import os
import json

class PhraseType(typing.TypedDict):
    phrase: str
    description: str
    example: str

class Phrase:
    def __init__(self, phrase, description, example):
        self.phrase = phrase
        self.description = description
        self.example = example
        self.date = None
    
    def get_date(self):
        return self.m_date
    
    def set_date(self, date):
        self.m_date = date

class PhraseGenerator:
    def __init__(self):
        print("initializing phrase generator")
        # key: phrase, value: phrase object
        self.m_used_phrases = {}
        self.m_phrases_queue = queue.Queue()
        self.m_todays_phrase = None
        self.m_last_three_phrases = []
        self._fill_queue()
    
    def _fill_queue(self, retries=0):
        # generate 100 phrases
        used_phrases_str = ""
        for key in self.m_used_phrases.keys():
            used_phrases_str += self.m_used_phrases[key].phrase
            used_phrases_str += ", "
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
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
        response = model.generate_content(prompt, generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=list[PhraseType]))
        response_json = json.loads(response.text + "\n")
        for entry in response_json:
            if 'phrase' not in entry or 'description' not in entry or 'example' not in entry: # if doesn't populate properly fail here
                    continue
            if not self.m_used_phrases.get(entry['phrase']):
                # add to dict
                phrase_object = Phrase(entry['phrase'], entry['description'], entry['example'])
                self.m_used_phrases[phrase_object.phrase] = phrase_object
                # add to queue
                self.m_phrases_queue.put(phrase_object)
        #check queue is not empty still
        if self.m_phrases_queue.empty():
            retries += 1
            if retries < 5:
                print("queue empty, retrying")
                self._fill_queue(retries)
        return


    def get_phrase_from_queue(self): # this is weird
        phrase = self.m_phrases_queue.get()
        if self.m_phrases_queue:
            self._fill_queue()
        return self.m_phrases_queue.get()
    
    def in_recent_phrases(self, date):
        for phrase in self.m_last_three_phrases:
            if phrase.date == date:
                return phrase
        return None
    
    def add_to_recents(self, todays_phrase):
        if len(self.m_last_three_phrases) < 3:
            self.m_last_three_phrases.append(todays_phrase)
        oldest_index = 0
        for i in range(len(self.m_last_three_phrases)):
            if  self.m_last_three_phrases[i].date < self.m_last_three_phrases[oldest_index].date:
                oldest_index = i
        self.m_last_three_phrases[oldest_index] = todays_phrase

    def get_todays_phrase(self, date):
        todays_phrase = self.in_recent_phrases(date)
        if todays_phrase:
            return todays_phrase.phrase
        todays_phrase = self.get_phrase_from_queue()
        print("todays phrase: ", todays_phrase.phrase, todays_phrase.description, todays_phrase.example)
        todays_phrase.date = date
        self.add_to_recents(todays_phrase)
        return todays_phrase.phrase