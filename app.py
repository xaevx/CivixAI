import os
import traceback
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Initialize Flask app to serve static files from the current directory
app = Flask(__name__, static_folder='.', static_url_path='')

# Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = """You are CIVIX AI — an interactive assistant that helps users understand the Indian election process, timelines, and steps in a clear, engaging, and personalized way.

STRICT RULES:
1. Maintain strict neutrality and objectivity (no political bias, no partisan talking points).
2. Answer based on Indian democratic election processes (Election Commission of India rules, Lok Sabha, Vidhan Sabha) unless another specific jurisdiction is mentioned.
3. Structure your responses cleanly using Markdown headings, bullet points, and bold text.
4. If the user asks a question, ensure your response provides:
   - A Simple Explanation
   - A Step-by-Step Breakdown
   - A Timeline (if applicable to the question)
5. Adapt your response based on the requested mode:
   - "simple": Keep language accessible, concise, and easy to digest.
   - "deep": Provide a thorough "Deep Dive" with more context, historical background, or intricate procedural details.

Do NOT give medical, legal, or highly specific personalized advice. Stick to civic education.
"""

generation_config = {
  "temperature": 0.3,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        user_message = data.get('message', '')
        mode = data.get('mode', 'simple')
        history = data.get('history', [])
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config,
            system_instruction=SYSTEM_PROMPT + f"\n\nCURRENT MODE: {mode.upper()}",
        )
        
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(user_message)
        
        return jsonify({
            "response": response.text
        })
        
    except Exception as e:
        print(f"Error in /chat: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/election-data', methods=['POST'])
def get_election_data():
    try:
        data = request.get_json()
        election_type = data.get('type', 'general')
        state = data.get('state', '')
        
        context = f"the Indian General Election (Lok Sabha)"
        if election_type == 'state' and state:
            context = f"the state assembly election (Vidhan Sabha) in {state}, India"
            
        prompt = f"""
You are an expert electoral data analyst. Provide realistic (or projected) statistical data and timelines for {context}.
"""

        json_generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 1024,
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "nextElection": {"type": "string"},
                    "registeredVoters": {"type": "string"},
                    "turnoutGoal": {"type": "string"},
                    "turnout": {
                        "type": "object",
                        "properties": {
                            "labels": {"type": "array", "items": {"type": "string"}},
                            "data": {"type": "array", "items": {"type": "number"}}
                        }
                    },
                    "partySeats": {
                        "type": "object",
                        "properties": {
                            "labels": {"type": "array", "items": {"type": "string"}},
                            "data": {"type": "array", "items": {"type": "number"}}
                        }
                    },
                    "timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string"},
                                "event": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["nextElection", "registeredVoters", "turnoutGoal", "turnout", "partySeats", "timeline"]
            }
        }

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=json_generation_config,
        )
        
        response = model.generate_content(prompt)
        
        # Extract json using regex in case there is arbitrary surrounding text
        import re
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            raw_text = match.group(0)
        else:
            raw_text = response.text
        
        print("RAW JSON:", repr(raw_text))
        
        import json
        import ast
        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError as e:
            print("Standard JSON parsing failed, attempting fallback...")
            try:
                # Replace unquoted keys, single quotes, and JS constants
                import re
                clean_text = re.sub(r'(\w+)\s*:', r'"\1":', raw_text)
                clean_text = clean_text.replace("'", '"')
                clean_text = clean_text.replace("True", "true").replace("False", "false").replace("None", "null")
                result = json.loads(clean_text)
            except Exception as eval_e:
                raise Exception(f"Failed to parse AI output. JSON Error: {str(e)}. Fallback Error: {str(eval_e)}.")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in /api/election-data: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Civix AI server...")
    print("Access the app at: http://localhost:5000")
    app.run(debug=True, port=5000)
