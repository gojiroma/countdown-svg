from flask import Flask, send_file
import random
import re
from io import BytesIO
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

JST = timezone(timedelta(hours=9))

def random_pastel_color():
    r = random.randint(180, 255)
    g = random.randint(180, 255)
    b = random.randint(180, 255)
    return f"rgb({r},{g},{b})"

def generate_countdown_svg(target_date_str, event_name, width=300, height=160):
    target_dt = datetime.strptime(target_date_str, '%Y%m%d').replace(tzinfo=JST)
    now = datetime.now(JST)
    delta = target_dt - now

    if delta.days > 30:
        countdown_text = f"{delta.days}日"
        event_phrase = f"{event_name}まで"
    elif delta.days >= 0:
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        countdown_text = f"{delta.days}日{hours}時間{minutes}分"
        event_phrase = f"{event_name}まで"
    elif delta.days == 0 and delta.seconds >= 0:
        countdown_text = "当日"
        event_phrase = f"{event_name}まで"
    else:
        abs_delta = now - target_dt
        days = abs_delta.days
        hours = abs_delta.seconds // 3600
        minutes = (abs_delta.seconds % 3600) // 60
        countdown_text = f"{days}日{hours}時間{minutes}分"
        event_phrase = f"{event_name}から"

    bg_color = random_pastel_color()
    event_font_size = 30
    countdown_font_size = 36

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
        <text x="{width/2}" y="120" class="countdown">{countdown_text}</text>
    </svg>"""
    return svg_content

@app.route('/<path:path>')
def countdown_svg(path):
    parts = path.split('/')
    yyyymmdd = None
    event_name = None

    for part in parts:
        if re.fullmatch(r'\d{8}', part):
            yyyymmdd = part
        else:
            event_name = part

    if not yyyymmdd or not event_name:
        return "Invalid URL format. Use /YYYYMMDD/event_name or /event_name/YYYYMMDD", 400

    svg = generate_countdown_svg(yyyymmdd, event_name)
    svg_io = BytesIO(svg.encode('utf-8'))
    return send_file(svg_io, mimetype='image/svg+xml', as_attachment=False)

if __name__ == '__main__':
    app.run(port=5003, debug=True)
