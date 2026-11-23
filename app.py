import os
from flask import Flask, send_from_directory
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    df = pd.read_csv("data/clean_artworks.csv")
    report = open("data/eda_report.txt", encoding="utf-8").read()
    table = df.head(50).to_html(index=False)

    # charts folder ki saari PNG images
    chart_files = sorted(f for f in os.listdir("data/charts") if f.endswith(".png"))
    charts_html = "".join(
        f'<img src="/charts/{name}" style="max-width:100%; margin:10px 0;"><br>'
        for name in chart_files
    )

    return f"""
    <h1>The Provenance</h1>
    <p>Total artworks: {len(df)}</p>
    <h2>Charts</h2>{charts_html}
    <h2>EDA Report</h2><pre>{report}</pre>
    <h2>Sample Data</h2>{table}
    """

@app.route("/charts/<name>")
def chart(name):
    return send_from_directory("data/charts", name)