# Watertable
## Analysis and visualization of an observational well on North Pender Island

The well is solar-powered with a 4G connection; it has a depth sensor at the base that sends measurements every hour on the hour.
It's been running since 2003.
Data is sourced from the government of British Columbia's [Aquarius project](https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-science-data/water-data-tools/real-time-water-data-reporting).
This project graphs the current year's data, with the 95% historical range as a backdrop.
Key numbers (current water level, historical average for this time of year) is presented in easy-to-read text.

The project is hosted on Cloudflare, and is located at [watertable.nove.dev](https://watertable.nove.dev)

For more details, open the `main.ipynb` document. 
The most recent code is in generate.py, and that's what's used to update the website, but the notebook has useful information.
GitHub's Jupyter notebook rendering is a little flaky, so you may have to run it in your local installation.
