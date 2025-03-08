import streamlit as st
from phrase_generation import PhraseGenerator
from datetime import date
import asyncio

async def fetch_phrase():
    phraseGenerator = PhraseGenerator()
    todays_date = date.today()
    phrase = phraseGenerator.get_todays_phrase(todays_date)
    return phrase

def main():
    phrase = asyncio.run(fetch_phrase())
    st.markdown("# " + phrase['phrase'])
    st.markdown("## " + phrase['description'])
    st.markdown("### " + phrase['example'])
    
main()