import os
import re
import html
import requests
import pandas as pd
from flask import Flask, Response, send_from_directory

app = Flask(__name__)


@app.route("/")
def home():
    df = pd.read_csv("data/clean_artworks.csv")
    report = open("data/eda_report.txt", encoding="utf-8").read()

    chart_files = sorted(f for f in os.listdir("data/charts") if f.endswith(".png"))
    charts_html = "".join(
        f'<img src="/charts/{n}" style="max-width:100%; margin:10px 0;"><br>'
        for n in chart_files
    )

    # sirf woh artworks jin ki image_id maujood hai
    with_img = df[df["image_id"].notna()]
    sample = with_img.sample(min(24, len(with_img)))
    gallery_html = "".join(
        f'''<div style="width:220px; margin:10px;">
              <div style="height:220px; background:#eee; border-radius:8px; display:flex;
                          align-items:center; justify-content:center; color:#888; font-size:13px;
                          position:relative; overflow:hidden;">
                Image unavailable
                <img src="/img/{row["image_id"]}" loading="lazy" onerror="this.remove()"
                     style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover;">
              </div>
              <p style="font-size:14px;">{html.escape(str(row.get("title", "")))}</p>
            </div>'''
        for _, row in sample.iterrows()
    )

    return f"""
    <h1>The Provenance</h1>
    <p>Total artworks: {len(df)}</p>
    <h2>Gallery</h2>
    <div style="display:flex; flex-wrap:wrap;">{gallery_html}</div>
    <h2>Charts</h2>{charts_html}
    <h2>EDA Report</h2><pre>{html.escape(report)}</pre>
    """


@app.route("/charts/<name>")
def chart(name):
    return send_from_directory("data/charts", name)


@app.route("/img/<image_id>")
def img(image_id):
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", image_id):
        return Response(status=404)

    url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "the_provenance-student-project/1.0"},
            timeout=8,
        )
        if r.status_code == 200:
            return Response(
                r.content,
                mimetype="image/jpeg",
                headers={"Cache-Control": "public, max-age=86400"},
            )
    except requests.RequestException:
        pass

    return Response(status=404)