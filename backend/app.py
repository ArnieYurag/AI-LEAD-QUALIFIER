from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend is running"
    })

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

    print("\n=== NEW LEAD===")
    print(data)
    print("==============\n")
    mock_result = {
        "score": 78,
        "label": "Warm",
        "summary": "Client has a clear project need, stated budget, and timeline. Worth following up."
    }

    return jsonify({
        # "status": "success",
        # "message": "Lead received",
        # "lead": data
        "status": "success",
        "message": "Lead analyzed successfully",
        "lead": data,
        "result": mock_result
    })


if __name__ == "__main__":
    app.run(debug=True)
