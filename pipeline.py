from datetime import datetime
from typing import Iterator, List, Tuple
from statistics import mean
import numpy as np


def clean_and_process(stamp: str, value: str, code: str):
    try:
        if int(code) < -1:
            return False
    except ValueError:
        return False
    if stamp[5:10] == "02-29":  # janky hack, mate!
        return False  # 😭
    elif int(stamp[:4]) < 2003:
        return False
    depth = float(value) * 3.28  # metres to feet conversion
    if depth > 40:
        return False
    date = datetime.fromisoformat(stamp)
    return (date, -depth)


def year_splitter(
    days: Iterator[Tuple[datetime, float]]
) -> List[List[Tuple[datetime, float]]]:
    current_year = datetime.today().year
    years = [[] for _ in range(current_year - 2003 + 1)]
    for day in days:
        years[day[0].year - 2003].append(day)
    return years


def unify_year(dates: List[Tuple[datetime, float]]):
    year = datetime.today().year
    unified_dates = []
    for date in dates:
        unified_dates.append((date[0].replace(year=year), date[1]))
    return unified_dates


def rolling_mean(x, N):
    return np.convolve(x, np.ones((N,)) / N)[(N - 1) :]


def historical_past_two_weeks(years: List[List[Tuple[datetime, float]]]) -> float:
    now = datetime.now()
    return mean(
        # average out all years
        map(
            # map each year to the average level at this time
            lambda year: mean(
                # take the average across all salient days
                map(
                    # only use the water level
                    lambda day: day[1],
                    # all times within 7 days in either direction of right now
                    filter(
                        lambda day: abs((day[0] - now).days) < 7, np.transpose(year)
                    ),
                )
            ),
            years,
        )
    )


def rough_date() -> str:
    now = datetime.now()
    month = now.strftime("%B")
    prefix = "early " if now.day < 10 else "mid-" if now.day < 20 else "late "
    return prefix + month
