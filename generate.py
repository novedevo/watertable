import requests as rq
import datetime
import polars as pl
import seaborn as sns
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

now = datetime.datetime.now(ZoneInfo("America/Vancouver"))
current_year = now.year

params = {
    "DataSet": "SGWL.Working@OW283",
    "DateRange": "EntirePeriodOfRecord",
    # 'StartTime': "2021-01-01 00:00:00",
    "ExportFormat": "csv",
    "Compressed": "false",
    "RoundData": "False",
    "Unit": "306",  # 228 is feet,, the API ignores this, even internally
    "Timezone": "-7",
}

token = rq.post(
    url="https://aqrt.nrs.gov.bc.ca/Export/DataSetToken", params=params
).json()["Token"]
params["Token"] = token

response = rq.get(url="https://aqrt.nrs.gov.bc.ca/Export/DataSet", params=params)

df = pl.read_csv(
    response.content,
    try_parse_dates=True,
    skip_lines=5,
    new_columns=["timestamp", "level"],
)
df = df.drop_nans()
df = df.group_by_dynamic("timestamp", every="1d").agg(pl.col("level").mean())
df = df.with_columns(
    (pl.col("level") * -3.28), (pl.col("timestamp").dt.year()).alias("year")
)
df = df.remove(
    (pl.col("timestamp").dt.month() == 2) & (pl.col("timestamp").dt.day() == 29)
)
df = df.with_columns(
    (pl.col("timestamp").dt.replace(year=current_year)),
    (pl.col("year") == current_year).alias("current_year"),
)
df = df.remove((pl.col("year") < 2004))

previous_years = df.filter(~pl.col("current_year"))
redline = df.filter(pl.col("current_year"))

ordinal_today = now.date().replace(year=1).toordinal()
historical_average: float = -(
    previous_years.filter(
        (pl.col("timestamp").dt.ordinal_day() - ordinal_today).abs() <= 7
    )
    .group_by("year")
    .agg(pl.col("level").mean())
    .mean()["level"]
    .item()
)
current_level: float = -redline.row(-1, named=True)["level"]

fig, ax = plt.subplots()
fig.set_size_inches(14, 10)
sns.lineplot(
    ax=ax,
    data=previous_years,
    x="timestamp",
    y="level",
    color="teal",
    errorbar=("pi", 90),
    linewidth=0,
)
sns.lineplot(data=redline, x="timestamp", y="level", ax=ax, color="blue")
handles = [
    Patch(facecolor="teal", alpha=0.3, label="historical range"),
    Line2D([0], [0], color="blue", label=f"{current_year}"),
]

ax.legend(handles=handles)
ax.set_xlabel("")
ax.set_ylabel("feet below the surface")
ax.set_title("North Pender Island Water Table Status")
ax.set_xlim(datetime.date(current_year, 1, 1), datetime.date(current_year, 12, 31))  # type: ignore[arg-type]

locator = mdates.AutoDateLocator(minticks=3, maxticks=20)
formatter = mdates.ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

fig.savefig("www/output.svg")
fig.set_size_inches(7, 5)
fig.savefig("www/output_small.svg")

def rough_date() -> str:
    month = now.strftime("%B")
    prefix = "early " if now.day < 10 else "mid-" if now.day < 20 else "late "
    return prefix + month

with open("index.html") as index:
    index = index.read().replace("XX", now.strftime("%Y-%m-%d, %H:%M PT"), 1)
    index = index.replace("XX", ("%2.1f" % current_level), 1)
    index = index.replace("XX", ("%2.1f" % historical_average), 1)
    index = index.replace("this time of year", rough_date())
with open("www/index.html", "w") as new_index:
    new_index.write(index)

with open("www/output.svg") as graph:
    graph = (
        graph.read()
        .replace(
            """<g id="patch_1">
   <path d="M 0 720
L 1008 720
L 1008 0
L 0 0
z
" style="fill:none;"/>
  </g>""",
            "",
        )
        .replace('viewBox="0 0 1008 720"', 'viewBox="80 60 840 620"')
        .replace('height="720pt"', "")
        .replace('width="1008pt"', "")
    )
with open("www/output.svg", "w") as new_graph:
    new_graph.write(graph)
with open("www/output_small.svg") as graph:
    graph = (
        graph.read()
        .replace(
            """  <g id="patch_1">
   <path d="M 0 360
L 504 360
L 504 0
L 0 0
z
" style="fill:none;"/>
  </g>""",
            "",
        )
        .replace('viewBox="0 0 504 360"', 'viewBox="15 20 445 330"')
        .replace('height="360pt"', "")
        .replace('width="504pt"', "")
    )
with open("www/output_small.svg", "w") as new_graph:
    new_graph.write(graph)
