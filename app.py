from flask import Flask, render_template_string, send_file
import pandas as pd
import json
import os
import qrcode

# ================= CONFIG =================
EXCEL_FILE = "reviews.xlsx"
STATE_FILE = "state.json"
QR_FILE = "ketli_chai_qr.png"

GOOGLE_REVIEW_URL = "https://search.google.com/local/writereview?placeid=ChIJf9Eqc1XJ5zsRIG-fZCU6TTk"

app = Flask(__name__)

# ================= QR GENERATION =================
def generate_qr(app_url):
    if not app_url or os.path.exists(QR_FILE):
        return
    qr = qrcode.QRCode(
        version=6,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000", back_color="#fff")
    img.save(QR_FILE)

# ================= REVIEW ROTATION =================
def get_next_review():
    if not os.path.exists(EXCEL_FILE):
        return "Amazing chai with strong flavour and authentic old Mumbai vibes. Must visit Ketli Chai!"
    df = pd.read_excel(EXCEL_FILE)
    state = {"last_index": 0}
    if os.path.exists(STATE_FILE):
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
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    generate_qr(render_url)

    review = get_next_review()
    if not review:
        return "<h2 style='text-align:center;'>🙏 All reviews completed. Thank you!</h2>"

    return render_template_string(f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ketli Chai | Since 1998</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    min-height: 100vh;
}}

.overlay {{
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}}

.card {{
    width: 100%;
    max-width: 420px;
    background: rgba(255,255,255,0.95);
    border-radius: 24px;
    padding: 26px;
    box-shadow: 0 30px 80px rgba(0,0,0,0.45);
    animation: fadeIn 0.6s ease;
}}

@keyframes fadeIn {{
    from {{ opacity:0; transform:translateY(20px); }}
    to {{ opacity:1; transform:translateY(0); }}
}}

.brand {{
    text-align: center;
}}

.brand h1 {{
    margin: 0;
    font-size: 32px;
    color: #5a2d0c;
}}

.brand span {{
    font-size: 14px;
    color: #777;
}}

.badges {{
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin: 18px 0;
}}

.badge {{
    background: #ffedd5;
    color: #7c2d12;
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 13px;
}}

textarea {{
    width: 100%;
    height: 140px;
    border-radius: 18px;
    padding: 14px;
    font-size: 15px;
    border: 1px solid #ddd;
    resize: none;
}}

button {{
    width: 100%;
    margin-top: 16px;
    padding: 18px;
    border-radius: 18px;
    border: none;
    background: linear-gradient(135deg,#ff9800,#ff5722);
    color: #fff;
    font-size: 17px;
    font-weight: 600;
    cursor: pointer;
}}

.secondary {{
    background: #f3f4f6;
    color: #111;
    margin-top: 10px;
}}

.note {{
    text-align: center;
    font-size: 13px;
    color: #555;
    margin-top: 12px;
}}

.footer {{
    text-align: center;
    font-size: 12px;
    color: #666;
    margin-top: 14px;
}}
</style>
</head>

<body>
<div class="overlay">
<div class="card">

<div class="brand">
<h1>☕ Ketli Chai</h1>
<span>Serving Mumbai Since 1998</span>
</div>

<div class="badges">
<div class="badge">🍋 Lemon Tea</div>
<div class="badge">🏺 Kullad Chai</div>
<div class="badge">🔥 Special Tea</div>
</div>

<textarea id="review">{review}</textarea>

<button onclick="copyAndGo()">⭐ Review Copied • Open Google</button>
<button class="secondary" onclick="manualCopy()">📋 Copy Again</button>

<div class="note">
Review is already copied. Just <b>Paste</b> on Google and submit ⭐
</div>

<div class="footer">
❤️ Trusted by generations
</div>

</div>
</div>

<script>
window.onload = function() {{
    autoCopy();
    setTimeout(openGoogle, 1200);
}}

function autoCopy() {{
    let t = document.getElementById("review");
    t.select();
    document.execCommand("copy");
}}

function manualCopy() {{
    autoCopy();
    alert("Review copied again 👍");
}}

function openGoogle() {{
    window.open("{GOOGLE_REVIEW_URL}", "_blank");
}}

function copyAndGo() {{
    autoCopy();
    openGoogle();
}}
</script>

</body>
</html>
""")

@app.route("/qr")
def qr():
    if not os.path.exists(QR_FILE):
        return "QR not generated yet"
    return send_file(QR_FILE, mimetype="image/png")

# ================= START =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
