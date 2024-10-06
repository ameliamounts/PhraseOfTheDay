# Generate phrases via the gemini API
# Store them in a date dictionary or a set? 
# Could queue them and the pop them off the queue
# Save them in a set and check if in set before adding to the queue

# Retrieve json of phrases

# Parse Json of phrases into a set and queue

# Hold the list somewhere outside of the program so when it starts up 
# it doesn't repeat the phrasess that have already been used, then will need to insert them into the set upon runtime?

import queue
from datetime import date
import google.generativeai as genai
import typing_extensions as typing
import os
import json

# test_data = [{"description": "To be in a brown study", "example": "She sat in a brown study, lost in thought.", "phrase": "in a brown study"}, 
#             {"description": "To be in a pickle", "example": "He was in a pickle after losing his keys.", "phrase": "in a pickle"}, 
#             {"description": "To be in a stew", "example": "I'm in a stew about the upcoming exam.", "phrase": "in a stew"}, 
#             {"description": "To have a whale of a time", "example": "We had a whale of a time at the party.", "phrase": "whale of a time"}, 
#             {"description": "To be in a fix", "example": "He was in a fix after forgetting his passport.", "phrase": "in a fix"}, 
#             {"description": "To be a bit of a handful", "example": "The new puppy is a bit of a handful.", "phrase": "a bit of a handful"}, 
#             {"description": "To be all at sea", "example": "He felt all at sea after moving to a new city.", "phrase": "all at sea"}, 
#             {"description": "To be up the creek", "example": "He's up the creek without a paddle now that his car has broken down.", "phrase": "up the creek"}, 
#             {"description": "To be in a spot", "example": "He was in a spot after accidentally revealing the surprise.", "phrase": "in a spot"}, 
#             {"description": "To be in a tizzy", "example": "She was in a tizzy trying to find her lost keys.", "phrase": "in a tizzy"}, 
#             {"description": "To be in a quandary", "example": "He was in a quandary about which job to accept.", "phrase": "in a quandary"}, 
#             {"description": "To be in a blue funk", "example": "He's been in a blue funk ever since his girlfriend left him.", "phrase": "in a blue funk"}, 
#             {"description": "To be on the horns of a dilemma", "example": "She was on the horns of a dilemma about whether to stay or leave.", "phrase": "on the horns of a dilemma"}, 
#             {"description": "To be in a flap", "example": "I was in a flap when I realized I forgot my phone.", "phrase": "in a flap"}, 
#             {"description": "To be in a lather", "example": "He was in a lather after having to give a speech.", "phrase": "in a lather"}, 
#             {"description": "To be in a fog", "example": "He was in a fog after the car accident.", "phrase": "in a fog"}, 
#             {"description": "To be in a bind", "example": "He was in a bind after his car broke down on the way to the airport.", "phrase": "in a bind"}, 
#             {"description": "To be in a state", "example": "He was in a state after his team lost the championship.", "phrase": "in a state"}, 
#             {"description": "To be in a right old mess", "example": "The kitchen was in a right old mess after the party.", "phrase": "in a right old mess"}, 
#             {"description": "To be in a hole", "example": "He's in a hole financially after losing his job.", "phrase": "in a hole"}]

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

