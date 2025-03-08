class Phrase:
    def __init__(self, phrase, description, example):
        self.dict = {
            "phrase" : phrase,
            "description" : description,
            "example" : example
        }
        self.date = None
    
    def get_date(self):
        return self.date
    
    def set_date(self, date):
        self.date = date
    
    def get_phrase(self):
        return self.dict["phrase"]
    
    def get_example(self):
        return self.dict["example"]
    
    def get_description(self):
        return self.dict["description"]
    
    def to_dict(self):
        return self.dict