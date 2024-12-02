# Crypto AI Agent 🤖💰

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

1. Clone the repository:
 git clone https://github.com/your-repo/crypto-ai-agent.git
 cd crypto-ai-agent
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Add your API keys to secrets.toml:

plaintext
Copy code
[togetherai]
api_key = "YOUR_TOGETHER_AI_API_KEY"

[coinapi]
api_key = "YOUR_COINAPI_API_KEY"
Running the App ▶️
Start the Streamlit app:

bash
Copy code
streamlit run app.py
Open your browser and navigate to http://localhost:8501.

API Integrations 🔗
Together AI: Powers the LLaMA 3.1 8B model for natural language understanding and responses.
CoinAPI: Fetches real-time cryptocurrency price data.
Technical Stack 🛠️
Frontend: Streamlit
Backend: Python
APIs: Together AI, CoinAPI
File Structure 📁
plaintext
Copy code
crypto-ai-agent/
├── app.py             # Main application script
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
└── secrets.toml       # API keys (not tracked in version control)
Contributing 🤝
Contributions are welcome! If you'd like to improve the app or add new features, please follow these steps:

Fork the repository.
Create a feature branch:
bash
Copy code
git checkout -b feature-name
Commit your changes:
bash
Copy code
git commit -m "Add feature-name"
Push to your fork:
bash
Copy code
git push origin feature-name
Submit a pull request.
License 📜
This project is licensed under the MIT License.

Contact 📧
For questions or support, please reach out to your-email@example.com.

markdown
Copy code

### Adjustments for Your Project:

1. Replace `your-repo` with the actual repository name.
2. Replace `your-email@example.com` with your contact email.
3. Update the license section if you're using a different license.

Let me know if you need further customization or enhancements! 😊
