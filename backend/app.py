from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import json
import csv

load_dotenv ()
app = Flask(__name__)
CORS(app)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("GROQ API KEY LOADED:", bool(GROQ_API_KEY))

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend is running"
    })
def extract_json(content):
    start = content.find("{")
    end = content.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in AI response")
    return json.loads(content[start:end])
def analyze_lead_with_ai(lead_data):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
You are a lead qualification assistant.
Analyze this lead and return ONLY valid JSON in this exact format:
{{
  "score": 75,
  "label": "Warm",
  "summary": "Short explanation here"
}}
Lead details:
Name: {lead_data['name']}
Email: {lead_data['email']}
Budget: {lead_data['budget']}
Timeline: {lead_data['timeline']}
Description: {lead_data['description']}
Rules:
- score must be a number from 0 to 100
- Higher score if budget is clear, timeline is clear, and project description is specific
- Label must be exactly one of: Hot, Warm, Cold
- Hot = very promising lead
- Warm = somewhat promising but needs follow-up
- Cold = weak or unclear lead
- return JSON only
"""
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print ("STATUS CODE:", response.status_code)
    # print ("RAW RESPONSE:", response.text)
    response.raise_for_status()
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    return extract_json(content)
def send_to_webhook(lead_data, ai_result):
    webhook_url = "YOUR_WEBHOOK_URL_HERE"

    payload = {
        "name": lead_data["name"],
        "email": lead_data["email"],
        "budget": lead_data["budget"],
        "timeline": lead_data["timeline"],
        "description": lead_data["description"],
        "score": ai_result["score"],
        "label": ai_result["label"],
        "summary": ai_result["summary"]
    }

    response = requests.post(webhook_url, json=payload, timeout=15)
    response.raise_for_status()

def save_lead_to_csv(lead_data, ai_result):
    file_path = "leads.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "name",
                "email",
                "budget",
                "timeline",
                "description",
                "score",
                "label",
                "summary"
            ])

        writer.writerow([
            lead_data["name"],
            lead_data["email"],
            lead_data["budget"],
            lead_data["timeline"],
            lead_data["description"],
            ai_result["score"],
            ai_result["label"],
            ai_result["summary"]
        ])

@app.route("/qualify-lead", methods=["POST"])
def qualify_lead():
    data = request.get_json()
    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data received"
        }), 400
    required_fields = ["name", "email", "budget", "timeline", "description"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({
            "status": "error",
            "message": "Missing required fields",
            "missing_fields": missing_fields
        }), 400
    
    try:
        ai_result = analyze_lead_with_ai(data)
        print ("FINAL AI RESULT:", ai_result)
        save_lead_to_csv(data, ai_result)
        return jsonify({
            "status": "success",
            "message": "Lead analyzed successfully",
            "lead": data,
            "result": ai_result
        })
    except Exception as e:
        print("AI ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": "AI analysis failed",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
