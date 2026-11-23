    type: 'bar',
    data: { labels: d.labels, datasets: [{ data: d.values, backgroundColor: palette, borderRadius: 2, maxBarThickness: 25 }] },
    options: {
      responsive: true,
      indexAxis: horizontal ? 'y' : 'x',
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: horizontal ? grid : { display: false }, ticks: { color: '#82796b' } },
        y: { grid: horizontal ? { display: false } : grid, ticks: { color: '#82796b' } }
      }
    }
  });
}
bar('c1', D.countries, false);
new Chart(document.getElementById('c2'), {
  type: 'line',
  data: { labels: D.centuries.labels, datasets: [{
    data: D.centuries.values, borderColor: '#566653',
    backgroundColor: 'rgba(179,154,105,.22)', fill: true, tension: .35,
    pointBackgroundColor: '#b39a69', pointBorderColor: '#fbf8f0', pointBorderWidth: 2, pointRadius: 4
  }] },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { x: { grid: { display: false } }, y: { grid } }
  }
});
bar('c3', D.departments, true);
bar('c4', D.artists, true);
</script>
</body>
</html>
"""


@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    country = request.args.get("country", "").strip()
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1

    with_img = df[df["image_id"].notna()]
    view = with_img
    if q:
        mask = (
            view["title"].str.contains(q, case=False, na=False, regex=False)
            | view["artist_title"].str.contains(q, case=False, na=False, regex=False)
        )
        view = view[mask]
    if country:
        view = view[view["place_of_origin"] == country]

    total = len(view)
    pages = max(1, math.ceil(total / PER_PAGE))
    page = min(page, pages)
    items = view.iloc[(page - 1) * PER_PAGE: page * PER_PAGE].to_dict("records")

    featured = with_img.sample(1).iloc[0].to_dict()

    known_countries = df["place_of_origin"][df["place_of_origin"] != "Unknown"]
    countries = list(known_countries.value_counts().head(40).index)

    years = df["date_start"].dropna()
    stats = {
        "total": len(df),
        "countries": int(known_countries.nunique()),
        "artists": int(df["artist_title"][df["artist_title"] != "Unknown"].nunique()),
        "span": f"{int(years.min())}-{int(years.max())}" if len(years) else "N/A",
    }

    charts = {
        "countries": top(df["place_of_origin"]),
        "centuries": century_counts(),
        "departments": top(df["department_title"]),
        "artists": top(df["artist_title"]),
    }

    try:
        report = open("data/eda_report.txt", encoding="utf-8").read()
    except FileNotFoundError:
        report = "EDA report not found."
    try:
        chart_files = sorted(f for f in os.listdir("data/charts") if f.endswith(".png"))
    except FileNotFoundError:
        chart_files = []

    return render_template_string(
        TEMPLATE, stats=stats, charts=charts, items=items, total=total,
        page=page, pages=pages, q=q, country=country, countries=countries,
        report=report, chart_files=chart_files, featured=featured,
    )


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


if __name__ == "__main__":
    app.run(debug=True)
