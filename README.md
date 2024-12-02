

# Crypto AI Agent 🤖💰
## Crypto Ai Agent https://cryptofetch.streamlit.app/
The **Crypto AI Agent** is an interactive chatbot powered by **LLaMA 3.1 8B** and **CoinAPI**. It provides real-time cryptocurrency price updates and handles general queries. The bot supports multiple currencies and can process inputs in various languages, responding in English.

---

## Features 🌟

- 💰 **Real-Time Cryptocurrency Prices**: Fetch prices for popular cryptocurrencies like Bitcoin, Ethereum, and Litecoin.
- 🌍 **Multi-Currency Support**: Ask for prices in USD, INR, EUR, and other common currencies.
- 🗣️ **Conversational AI**: Handles general queries and engages in meaningful conversations.
- 🌐 **Language Understanding**: Understands user inputs in various languages but responds in English.
- 🪄 **Interactive and User-Friendly**: Simple interface for a seamless user experience.

---

## Examples of What You Can Ask

- **"What's the price of Bitcoin?"**
- **"What's the price of Ethereum in rupees?"**
- **"Change language to Spanish."**
- **"¿Cuál es el precio de Litecoin?"**
- **"Tell me a joke."**
- **"How much is Bitcoin in EUR?"**

---

## Prompt Engineering Approach 🧠

The **Crypto AI Agent** uses carefully crafted prompts to deliver accurate, context-aware, and user-friendly responses.

### 1. **Conversation Context Management**
- Retains the last 10 exchanges to ensure coherent conversations.
- Formats exchanges with roles (`user` and `assistant`) and content.

### 2. **Prompt Template**
- Guides the AI's behavior with a structured system prompt:
Assistant: You are a helpful assistant capable of answering cryptocurrency-related queries and general questions. Always provide clear, accurate, and polite responses. User: <user-input> Assistant:

markdown
Copy code

### 3. **Handling Ambiguities**
- Translates non-English inputs to English using `googletrans`.
- Normalizes currencies like "rupees" → `INR`, "dollars" → `USD`.

### 4. **Dynamic Adjustments**
- Distinguishes between cryptocurrency queries and general queries.
- Responds dynamically based on the user's input.

### 5. **Temperature Tuning**
- Uses a `temperature` value of `0.7` to balance accuracy and conversational tone.

### 6. **Multi-Currency Support**
- Supports queries in USD, INR, EUR, and other common currencies.
- Maps currency names to ISO codes (e.g., "rupees" → `INR`).

### 7. **Error Handling**
- Provides clear feedback for ambiguous or unsupported queries:
- Example: "Sorry, I couldn't retrieve the price for Bitcoin right now. Please try again later."

---

## Setup and Installation 🚀

### Prerequisites

Ensure you have Python 3.8 or later installed on your system.

### Installation Steps

