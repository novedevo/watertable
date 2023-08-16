import requests as rq
import csv
import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pipeline import *


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
reader = csv.reader(response.text.splitlines())


# with open("data/dataset.csv") as data:
parsed = filter(lambda x: x, map(lambda x: clean_and_process(x[0], x[1]), reader))
split = year_splitter(parsed)
years = list(map(lambda x: np.transpose(unify_year(x)), split))


fig, ax = plt.subplots()
fig.set_size_inches(14, 10)

ax.set_ylabel("feet below the surface")
ax.set_title("North Pender Island Water Table Status")
ax.set_xlim(years[-1][0][0], years[0][0][-1])

# fancy automatic date labels along x axis
locator = mdates.AutoDateLocator(minticks=3, maxticks=20)
formatter = mdates.ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)

# chosen for linear perception and contrast with red
colourmap = mpl.colormaps['viridis'] # type: ignore

# graphing each year with its own label and colour along the viridis colourmap
year_plots = []
current_year = datetime.today().year
for i, year in enumerate(years[7:-1]):
    year_as_percentage = i / (current_year - 1 - 2010)
    (year_plot,) = ax.plot(
        year[0][:-40],
        rolling_mean(year[1], 40)[:-40],
        color=colourmap(1 - year_as_percentage),
        label=i + 2010,
    )
    year_plots.append(year_plot)

# current year
ax.plot(years[-1][0], years[-1][1], color="red", label=current_year)

ax.legend()


fig.savefig("www/output.svg")
fig.set_size_inches(7, 5)
fig.savefig("www/output_small.svg")

current_level = abs(years[-1][-1][-1])
historical = abs(historical_past_two_weeks(years))

with open("index.html") as index:
    index = index.read().replace("XX", ("%2.1f" % current_level), 1)
    index = index.replace("XX", ("%2.1f" % historical), 1)
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
        .replace('viewBox="0 0 1008 720"', 'viewBox="80 50 915 670"')
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
        .replace('viewBox="0 0 504 360"', 'viewBox="15 20 490 350"')
        .replace('height="360pt"', "")
        .replace('width="504pt"', "")
    )
with open("www/output_small.svg", "w") as new_graph:
    new_graph.write(graph)
