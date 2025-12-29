from flask import Flask, render_template_string, send_file, request
import pandas as pd
import json
import os
import qrcode

# ================= CONFIG =================
EXCEL_FILE = "reviews.xlsx"
STATE_FILE = "state.json"
ANALYTICS_FILE = "analytics.json"
QR_FILE = "ketli_chai_qr.png"

GOOGLE_REVIEW_URL = "https://search.google.com/local/writereview?placeid=ChIJf9Eqc1XJ5zsRIG-fZCU6TTk"

app = Flask(__name__)

# ================= QR GENERATION =================
def generate_qr(app_url):
    if os.path.exists(QR_FILE):
        return

    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(app_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(QR_FILE)

    print("✅ QR Code generated:", QR_FILE)

# ================= ANALYTICS =================
def log_event(event):
    if not os.path.exists(ANALYTICS_FILE):
        data = {"scans": 0, "copied": 0, "google_opened": 0}
    else:
        with open(ANALYTICS_FILE) as f:
            data = json.load(f)

    data[event] += 1

    with open(ANALYTICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ================= REVIEW ROTATION =================
def get_next_review():
    df = pd.read_excel(EXCEL_FILE)

    if not os.path.exists(STATE_FILE):
        state = {"last_index": 0}
    else:
        with open(STATE_FILE) as f:
            state = json.load(f)

    idx = state["last_index"]

    if idx >= len(df):
        return None

    review = str(df.iloc[idx]["review_text"])
    state["last_index"] += 1

    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

    return review

# ================= ROUTES =================
@app.route("/")
def home():
    log_event("scans")
    review = get_next_review()

    if not review:
        return "<h2 style='text-align:center;'>🙏 All reviews completed. Thank you!</h2>"

    return render_template_string(f"""
    <h2>Ketli Chai – Since 1998</h2>
    <textarea id="review" style="width:100%;height:120px;">{review}</textarea>
    <br><br>
    <button onclick="copy()">Copy Review</button>

    <script>
    function copy() {{
        let t = document.getElementById("review");
        t.select();
        document.execCommand("copy");

        fetch('/copied');
        setTimeout(() => {{
            fetch('/google');
            window.open("{GOOGLE_REVIEW_URL}", "_blank");
        }}, 1200);
    }}
    </script>
    """)

@app.route("/copied")
def copied():
    log_event("copied")
    return "ok"

@app.route("/google")
def google():
    log_event("google_opened")
    return "ok"

# ================= QR DOWNLOAD =================
@app.route("/qr")
def qr():
    return send_file(QR_FILE, mimetype="image/png")

# ================= START =================
if __name__ == "__main__":
    # Detect Render public URL
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if render_url:
        generate_qr(render_url)

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
