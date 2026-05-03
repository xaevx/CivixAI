# CIVIX AI

A futuristic, AI-powered election dashboard and interactive civic assistant. CIVIX AI provides real-time, personalized insights into the Indian electoral process (Lok Sabha & Vidhan Sabha) through a stunning glassmorphism interface and strict, unbiased data visualization.

## Features

- **Futuristic Glassmorphism UI**: A cutting-edge dark mode design with neon accents and CSS Grid layouts.
- **Dynamic Election Dashboard**: Automatically fetches and visualizes critical statistical data for Indian General Elections and State Assembly Elections.
- **Interactive Data Visualization**: Integrated `Chart.js` rendering dynamic Doughnut charts for **Party Seat Distributions** and Line charts for historical **Voter Turnout**.
- **Interactive Chat Assistant**: Features an AI chatbot with togglable "Simple Mode" and "Deep Dive" capabilities for easy-to-digest civic education.
- **Strict Neutrality**: The AI backend is aggressively prompted to maintain strict political neutrality, focusing purely on processes, statistics, and democratic education.
- **Robust AI Integration**: Powered by the cutting-edge `gemini-2.5-flash` model using Strict JSON Output schema enforcement for flawless data fetching.

## Tech Stack

- **Frontend**: HTML5, Vanilla CSS (Custom Glassmorphism), Vanilla JavaScript, `Chart.js`, `marked.js`
- **Backend**: Python (Flask)
- **AI Engine**: Google Gemini API (`gemini-2.5-flash`)

## Project Structure

```
/civic-guide-ai
  ├── index.html        # Main dashboard and UI layout
  ├── style.css         # Glassmorphism and responsive design styles
  ├── script.js         # Frontend logic, API fetching, and Chart configurations
  ├── app.py            # Flask backend & Gemini API routing
  ├── requirements.txt  # Python dependencies
  ├── .env              # Environment variables (API Keys)
  └── README.md
```

## Setup Instructions

1. **Ensure all files are in a single directory.**

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add Your Gemini API Key**
   Open the `.env` file and replace the dummy key with your actual Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_key_here
   ```
   *You can get an API key from Google AI Studio.*

## How to Run

1. Start the Flask development server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   [http://localhost:5000](http://localhost:5000)

## Example Usage

- **Dashboard Exploration**: Select "State Election" from the dropdown, choose a state (e.g., "Tamil Nadu"), and click **Analyze** to watch the UI instantly adapt with precise party seat data and historical turnout charts.
- **Chat Interface**: Ask the AI questions like *"How does the EVM process work?"* or *"What is the Model Code of Conduct?"*
- **Deep Dive**: Toggle the "Deep Dive" switch to get comprehensive, multi-layered explanations of complex constitutional processes.
