from flask import Flask, request, jsonify

app = Flask(__name__)

alerts_db = []

@app.route("/alert", methods=["POST"])
def receive_alert():
    data = request.json
    alerts_db.append(data)
    print("🚨 ALERT RECEIVED:", data)
    return jsonify({"status": "ok"})

@app.route("/alerts", methods=["GET"])
def get_alerts():
    return jsonify(alerts_db)

if __name__ == "__main__":
    app.run(debug=True)