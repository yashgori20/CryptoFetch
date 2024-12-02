import streamlit as st
import requests
import time
from cachetools import TTLCache, cached
from googletrans import Translator
import re
import logging

logging.basicConfig(level=logging.INFO)

translator = Translator()

if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

try:
    togetherai_api_key = st.secrets["togetherai"]["api_key"]
    coinapi_key = st.secrets["coinapi"]["api_key"]
except KeyError:
    st.error("API keys are missing. Please add them to st.secrets.")
    st.stop()

price_cache = TTLCache(maxsize=100, ttl=300)

last_api_call_time = 0
RATE_LIMIT_SECONDS = 1

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
        logging.info(f"CoinAPI Response Status Code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        rate = data.get('rate')
        if rate is not None:
            return rate
        else:
            logging.error(f"Rate not found in CoinAPI response: {data}")
            return None
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return f"An error occurred: {err}"

def generate_llama_response(conversation_history):
    logging.info(f"Sending conversation to LLaMA model: {conversation_history}")
    url = 'https://api.together.xyz/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {togetherai_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'meta-llama/LLaMA-3.1-8B-Instruct-Turbo',
        'messages': conversation_history,
        'max_tokens': 150,
        'temperature': 0.7,
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        logging.info(f"Together AI Response Status Code: {response.status_code}")
        logging.debug(f"Together AI Response Text: {response.text}")
        response.raise_for_status()
        data = response.json()
        generated_text = data['choices'][0]['message']['content']
        if generated_text:
            return generated_text.strip()
        else:
            logging.error(f"No output in Together AI response: {data}")
            return "I'm sorry, I couldn't process your request at the moment."
    except Exception as e:
        logging.exception("Exception occurred:")
        return "I'm sorry, I couldn't process your request at the moment."

def build_conversation():
    conversation = []
    for speaker, message in st.session_state.conversation[-10:]:
        role = 'assistant' if speaker == 'Agent' else 'user'
        conversation.append({'role': role, 'content': message})
    return conversation

def is_language_change_request(text):
    language_change_keywords = ['switch to', 'change language to', 'speak in']
    return any(keyword in text.lower() for keyword in language_change_keywords)

def translate_to_english(text):
    try:
        translated = translator.translate(text, dest='en')
        return translated.text
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text

def parse_crypto_query(user_input):
    crypto_pattern = r'\b(bitcoin|btc|ethereum|eth|litecoin|ltc)\b'
    fiat_pattern = r'\b(usd|dollar|dollars|eur|euro|euros|inr|rupee|rupees|gbp|pound|pounds|aud|cad|jpy|yen|cny|yuan)\b'
    crypto_match = re.search(crypto_pattern, user_input, re.IGNORECASE)
    fiat_match = re.search(fiat_pattern, user_input, re.IGNORECASE)
    crypto_symbol = None
    fiat_currency = 'USD'
    if crypto_match:
        crypto_name = crypto_match.group(0).lower()
        crypto_symbols = {
            'bitcoin': 'BTC', 'btc': 'BTC',
            'ethereum': 'ETH', 'eth': 'ETH',
            'litecoin': 'LTC', 'ltc': 'LTC'
        }
        crypto_symbol = crypto_symbols.get(crypto_name)
    if fiat_match:
        fiat_name = fiat_match.group(0).lower()
        fiat_currencies = {
            'usd': 'USD', 'dollar': 'USD', 'dollars': 'USD',
            'eur': 'EUR', 'euro': 'EUR', 'euros': 'EUR',
            'inr': 'INR', 'rupee': 'INR', 'rupees': 'INR',
            'gbp': 'GBP', 'pound': 'GBP', 'pounds': 'GBP',
            'aud': 'AUD', 'cad': 'CAD',
            'jpy': 'JPY', 'yen': 'JPY',
            'cny': 'CNY', 'yuan': 'CNY'
        }
        fiat_currency = fiat_currencies.get(fiat_name.lower(), 'USD')
    logging.info(f"Parsed crypto query - Symbol: {crypto_symbol}, Currency: {fiat_currency}")
    return crypto_symbol, fiat_currency

def handle_general_query(user_input):
    detected_lang = translator.detect(user_input).lang
    if detected_lang != 'en':
        user_input_translated = translate_to_english(user_input)
    else:
        user_input_translated = user_input
    st.session_state.conversation.append(('User', user_input_translated))
    conversation_history = build_conversation()
    response = generate_llama_response(conversation_history)
    logging.info(f"AI Model Response: {response}")
    st.session_state.conversation.append(('Agent', response))
    return response

def process_user_input(user_input):
    logging.info(f"Processing user input: {user_input}")
    if is_language_change_request(user_input):
        response = "I can understand your input in other languages, but I will respond in English."
        st.session_state.conversation.append(('User', user_input))
        st.session_state.conversation.append(('Agent', response))
        logging.info(f"Response: {response}")
        return response
    crypto_symbol, fiat_currency = parse_crypto_query(user_input)
    if crypto_symbol:
        price = get_crypto_price(crypto_symbol, fiat_currency)
        logging.info(f"Retrieved price: {price}")
        if isinstance(price, float):
            response = f"The current price of {crypto_symbol} is {price:.2f} {fiat_currency}."
        else:
            response = f"Sorry, I couldn't retrieve the price for {crypto_symbol}."
        st.session_state.conversation.append(('User', user_input))
        st.session_state.conversation.append(('Agent', response))
        logging.info(f"Response: {response}")
    else:
        response = handle_general_query(user_input)
    return response

st.set_page_config(page_title="Crypto AI Agent", page_icon="💬")
st.title("🤖 Crypto AI Bot")

st.markdown("""
Welcome to the **Crypto AI Agent**! This assistant can help you with:

- 💰 **Fetching current cryptocurrency prices** (e.g., Bitcoin, Ethereum, Litecoin)
- 🌍 **Support for multiple currencies**: Ask for prices in USD, INR, EUR, or other common currencies.
- 🗣️ **Handling general queries and conversations**
- 🌐 **Understanding inputs in other languages** (responses will be in English)

---
""")

with st.form(key='user_input_form', clear_on_submit=True):
    user_input = st.text_input("Type your message here:")
    submit_button = st.form_submit_button(label='Send')

if submit_button:
    if user_input.strip() != '':
        process_user_input(user_input)
        st.markdown("---")
        for speaker, message in st.session_state.conversation:
            if speaker == 'User':
                st.markdown(f"**🧑 You:** {message}")
            else:
                st.markdown(f"**🤖 Agent:** {message}")
    else:
        st.warning("Please enter a message.")

st.markdown("""
---
### Examples of what you can ask:

- **"What's the price of Bitcoin?"**
- **"What's the price of Ethereum in rupees?"**
- **"Change language to Spanish."**
- **"¿Cuál es el precio de Ethereum?"**
- **"Tell me a joke."**
- **"How much is Litecoin in EUR?"**

---
""")

st.markdown("Powered by 🤖 LLaMA 3.1 8B and 💱 CoinAPI")
