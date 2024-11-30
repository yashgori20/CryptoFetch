import streamlit as st
import requests
import time
from cachetools import TTLCache, cached
from googletrans import Translator
import os
import re

# Initialize translator
translator = Translator()

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ''

# Retrieve API keys from st.secrets
togetherai_api_key = st.secrets["togetherai"]["api_key"]
coinapi_key = st.secrets["coinapi"]["api_key"]

# Set up cache for cryptocurrency prices (cache for 5 minutes)
price_cache = TTLCache(maxsize=100, ttl=300)

# Rate limiting parameters
last_api_call_time = 0
RATE_LIMIT_SECONDS = 1  # Adjust according to API rate limits

def rate_limited_api_call(func):
    def wrapper(*args, **kwargs):
        global last_api_call_time
        elapsed = time.time() - last_api_call_time
        if elapsed < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - elapsed)
        result = func(*args, **kwargs)
        last_api_call_time = time.time()
        return result
    return wrapper

@cached(cache=price_cache)
@rate_limited_api_call
def get_crypto_price(crypto_symbol, fiat_currency="USD"):
    url = f'https://rest.coinapi.io/v1/exchangerate/{crypto_symbol}/{fiat_currency}'
    headers = {'X-CoinAPI-Key': coinapi_key}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if 'rate' in data:
            rate = data['rate']
            return rate
        else:
            return None
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 429:
            return "Rate limit exceeded. Please try again later."
        else:
            return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"

def generate_llama_response(prompt):
    url = 'https://api.together.xyz/api/llama'
    headers = {
        'Authorization': f'Bearer {togetherai_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'prompt': prompt,
        'max_tokens': 150,
        'temperature': 0.7,
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['output']
    except Exception as e:
        return "I'm sorry, I couldn't process your request at the moment."

def build_prompt():
    conversation = ""
    # Limit context to last 10 exchanges to manage token limits
    for speaker, message in st.session_state.conversation[-10:]:
        conversation += f"{speaker}: {message}\n"
    return conversation

def is_language_change_request(text):
    language_change_keywords = ['switch to', 'change language to', 'speak in']
    return any(keyword in text.lower() for keyword in language_change_keywords)

def translate_to_english(text):
    try:
        translated = translator.translate(text, dest='en')
        return translated.text
    except Exception:
        return text  # Return original if translation fails

def parse_crypto_query(user_input):
    # Simple regex patterns for cryptocurrency and fiat currencies
    crypto_pattern = r'\b(bitcoin|btc|ethereum|eth|litecoin|ltc)\b'
    fiat_pattern = r'\b(usd|eur|inr|gbp)\b'
    
    crypto_match = re.search(crypto_pattern, user_input, re.IGNORECASE)
    fiat_match = re.search(fiat_pattern, user_input, re.IGNORECASE)
    
    crypto_symbol = None
    fiat_currency = 'USD'  # Default fiat currency
    
    if crypto_match:
        crypto_name = crypto_match.group(0).lower()
        crypto_symbols = {'bitcoin': 'BTC', 'btc': 'BTC', 'ethereum': 'ETH', 'eth': 'ETH', 'litecoin': 'LTC', 'ltc': 'LTC'}
        crypto_symbol = crypto_symbols.get(crypto_name)
    
    if fiat_match:
        fiat_currency = fiat_match.group(0).upper()
    
    return crypto_symbol, fiat_currency

def handle_general_query(user_input):
    # Translate input if necessary
    detected_lang = translator.detect(user_input).lang
    if detected_lang != 'en':
        user_input_translated = translate_to_english(user_input)
    else:
        user_input_translated = user_input
    # Build prompt with context
    prompt = build_prompt() + f"User: {user_input_translated}\nAgent:"
    # Generate response using LLaMA model
    response = generate_llama_response(prompt)
    return response.strip()

def process_user_input(user_input):
    # Check for language change request
    if is_language_change_request(user_input):
        response = "I can understand your input in other languages, but I will respond in English."
        return response

    # Check for cryptocurrency queries
    crypto_symbol, fiat_currency = parse_crypto_query(user_input)
    if crypto_symbol:
        price = get_crypto_price(crypto_symbol, fiat_currency)
        if isinstance(price, float):
            response = f"The current price of {crypto_symbol} is {price:.2f} {fiat_currency}."
        else:
            response = f"Sorry, I couldn't retrieve the price for {crypto_symbol}."
    else:
        # Handle other queries with the AI model
        response = handle_general_query(user_input)
    return response

# Callback function to clear text input
def clear_text():
    st.session_state["user_input"] = ""

# Streamlit app layout
st.title("AI Agent")

user_input = st.text_input("You:", key='user_input')
if st.button("Send", on_click=clear_text):
    if user_input:
        response = process_user_input(user_input)
        st.session_state.conversation.append(('User', user_input))
        st.session_state.conversation.append(('Agent', response))
        # No need to clear user_input here; it's handled by the callback

if st.session_state.conversation:
    for speaker, message in st.session_state.conversation:
        if speaker == 'User':
            st.markdown(f"**You:** {message}")
        else:
            st.markdown(f"**Agent:** {message}")
