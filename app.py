from flask import Flask, send_file, render_template_string, request
import random
import re
from io import BytesIO
from datetime import datetime, timezone, timedelta
from urllib.parse import unquote

app = Flask(__name__)
JST = timezone(timedelta(hours=9))

def format_date(yyyymmdd):
    year = yyyymmdd[:4]
    month = yyyymmdd[4:6]
    day = yyyymmdd[6:8]
    return f"{year}/{month}/{day}"

def random_pastel_color():
    r = random.randint(180, 255)
    g = random.randint(180, 255)
    b = random.randint(180, 255)
    return f"rgb({r},{g},{b})"

def generate_countdown_svg(target_date_str, event_name, width=300, height=160):
    target_dt = datetime.strptime(target_date_str, '%Y%m%d').replace(tzinfo=JST)
    now = datetime.now(JST)
    delta = target_dt - now

    if delta.days > 0:
        if delta.days > 365:
            days = delta.days
            years = days // 365
            remaining_days = days % 365
            months = remaining_days // 30
            remaining_days = remaining_days % 30
            if years > 0:
                countdown_text = f"{years}年{months}か月{remaining_days}日"
            else:
                countdown_text = f"{days}日"
            event_phrase = f"{event_name}まで"
        else:
            countdown_text = f"{delta.days}日"
            event_phrase = f"{event_name}まで"
    elif delta.days == 0:
        if delta.seconds > 0:
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            countdown_text = f"{hours}時間{minutes}分"
            event_phrase = f"{event_name}まで"
        else:
            abs_delta = now - target_dt
            if abs_delta.days == 0:
                hours = abs_delta.seconds // 3600
                minutes = (abs_delta.seconds % 3600) // 60
                countdown_text = f"{hours}時間{minutes}分"
                event_phrase = f"{event_name}から"
            else:
                days = abs_delta.days
                years = days // 365
                remaining_days = days % 365
                months = remaining_days // 30
                remaining_days = remaining_days % 30
                if years > 0:
                    countdown_text = f"{years}年{months}か月{remaining_days}日"
                else:
                    countdown_text = f"{days}日"
                event_phrase = f"{event_name}から"
    else:
        abs_delta = now - target_dt
        days = abs_delta.days
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        remaining_days = remaining_days % 30
        if years > 0:
            countdown_text = f"{years}年{months}か月{remaining_days}日"
        else:
            countdown_text = f"{days}日"
        event_phrase = f"{event_name}から"

    bg_color = random_pastel_color()
    event_font_size = 28
    countdown_font_size = 32
    svg_content = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{bg_color}" />
        <style>
            .event {{
                font-family: 'Hiragino Sans', 'Meiryo', sans-serif;
                font-size: {event_font_size}px;
                font-weight: bold;
                fill: #333333;
                text-anchor: middle;
            }}
            .countdown {{
                font-family: 'Hiragino Sans', 'Meiryo', sans-serif;
                font-size: {countdown_font_size}px;
                font-weight: bold;
                fill: #333333;
                text-anchor: middle;
            }}
        </style>
        <text x="{width/2}" y="45" class="event">{event_phrase}</text>
        <text x="{width/2}" y="110" class="countdown">{countdown_text}</text>
    </svg>"""
    return svg_content

def generate_error_svg(width=300, height=160):
    bg_color = "#ffebee"
    svg_content = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="{bg_color}" />
        <style>
            .error {{
                font-family: 'Hiragino Sans', 'Meiryo', sans-serif;
                font-size: 16px;
                font-weight: bold;
                fill: #d32f2f;
                text-anchor: middle;
            }}
        </style>
        <text x="150" y="50" class="error">Invalid URL format</text>
        <text x="150" y="70" class="error" font-size="14">Use /YYYYMMDD/event_name</text>
        <text x="150" y="90" class="error" font-size="14">or /event_name/YYYYMMDD</text>
    </svg>"""
    return svg_content

@app.route('/favicon.ico')
def favicon():
    return '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="#ff69b4"/>
    <text x="50" y="60" font-family="Arial" font-size="40" text-anchor="middle" fill="white">⏳</text>
</svg>
''', 200, {'Content-Type': 'image/svg+xml'}

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Countdown SVG Generator</title>
    <link rel="icon" href="/favicon.ico" type="image/svg+xml">
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background-color: #f8f9fa;
            color: #333;
        }
        .container {
            text-align: center;
            width: 300px;
        }
        .inputs {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 20px;
        }
        input {
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #ff69b4;
        }
        input::placeholder {
            color: #adb5bd;
        }
        .preview-container {
            margin-bottom: 15px;
        }
        iframe {
            border: none;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: white;
            width: 300px;
            height: 160px;
        }
        button {
            padding: 10px 16px;
            background-color: #ff69b4;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
            width: 100%;
        }
        button:hover {
            background-color: #e91e63;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="inputs">
            <input type="text" id="date" placeholder="日付 (YYYYMMDD)" pattern="\\d{8}" autofocus>
            <input type="text" id="event" placeholder="イベント名">
        </div>
        <div class="preview-container">
            <iframe id="preview" width="300" height="160" frameborder="0"></iframe>
        </div>
        <button id="copyBtn" disabled>Copy URL</button>
    </div>
    <script>
        const dateInput = document.getElementById('date');
        const eventInput = document.getElementById('event');
        const preview = document.getElementById('preview');
        const copyBtn = document.getElementById('copyBtn');

        let debounceTimer;
        function updatePreview() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const date = dateInput.value;
                const eventName = eventInput.value;
                if (date && eventName) {
                    const url = `/${date}/${encodeURIComponent(eventName)}`;
                    preview.src = url;
                    copyBtn.disabled = false;
                    copyBtn.onclick = () => {
                        const fullUrl = `${window.location.origin}${url}`;
                        navigator.clipboard.writeText(fullUrl)
                            .then(() => {
                                copyBtn.textContent = 'Copied!';
                                setTimeout(() => {
                                    copyBtn.textContent = 'Copy URL';
                                }, 2000);
                            });
                    };
                } else {
                    copyBtn.disabled = true;
                }
            }, 300);
        }

        dateInput.addEventListener('input', updatePreview);
        eventInput.addEventListener('input', updatePreview);
    </script>
</body>
</html>
''')

@app.route('/<path:path>')
def countdown(path):
    parts = path.split('/')
    yyyymmdd = None
    event_name = None
    if len(parts) == 2 and re.fullmatch(r'\d{8}', parts[0]):
        yyyymmdd = parts[0]
        event_name = unquote(parts[1])
    elif len(parts) == 2 and re.fullmatch(r'\d{8}', parts[1]):
        yyyymmdd = parts[1]
        event_name = unquote(parts[0])
    if yyyymmdd and event_name:
        svg = generate_countdown_svg(yyyymmdd, event_name)
    else:
        svg = generate_error_svg()
    svg_io = BytesIO(svg.encode('utf-8'))
    return send_file(svg_io, mimetype='image/svg+xml', as_attachment=False)

if __name__ == '__main__':
    app.run(port=5003, debug=True)
