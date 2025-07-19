from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow frontend JS requests

# Blocked sites
blocked_sites = {"instagram.com", "facebook.com", "snapchat.com", "spotify.com"}

def is_break_time():
    now = datetime.now()
    return (now.hour == 13) or (now.hour == 16 and now.minute <= 15)

def is_work_time():
    now = datetime.now()
    return 9 <= now.hour < 20 and not is_break_time()

@app.route("/check-site", methods=["POST"])
def check_site():
    data = request.json
    qr = data.get("qr", "").strip().upper()
    site = data.get("site", "").strip().lower()

    if not qr.startswith("EMP") or not site:
        return jsonify({"allowed": False, "message": "❌ Invalid QR Code or site."}), 400

    if not site.startswith("http://") and not site.startswith("https://"):
        site = "http://" + site

    try:
        parsed = urlparse(site)
        domain = parsed.netloc.replace("www.", "").split(":")[0]

        if is_break_time():
            return jsonify({"allowed": True, "message": f"✅ Break time access granted to {domain}."})

        if is_work_time():
            if domain in blocked_sites:
                return jsonify({"allowed": False, "message": f"🚫 {domain} is blocked during work hours."}), 403
            return jsonify({"allowed": True, "message": f"✅ Access granted to {domain} during office time."})

        return jsonify({"allowed": False, "message": "⏱️ Outside office hours."}), 403

    except Exception as e:
        return jsonify({"allowed": False, "message": f"❌ Invalid URL: {str(e)}"}), 400

@app.route("/submit-reason", methods=["POST"])
def submit_reason():
    data = request.json
    reason = data.get("reason", "").strip()
    if not reason:
        return jsonify({"message": "❌ Reason cannot be empty."}), 400
    print(f"Submitted reason: {reason}")
    return jsonify({"message": "✅ Reason submitted for review."})

if __name__ == "__main__":
    app.run(debug=True)
