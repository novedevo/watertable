from datetime import datetime
from typing import Iterable, Iterator, List, Tuple
from statistics import mean
import numpy as np

now = datetime.now()


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


def get_average(days: List[Tuple[datetime, float]]) -> float:
    levels = map(lambda day: day[1], days)
    return mean(levels)


def trim_to_two_weeks(
    year: Iterable[Tuple[datetime, float]]
) -> List[Tuple[datetime, float]]:
    ret = list(filter(lambda day: get_difference(day[0]) < 7, year))
    if len(ret) < 5:
        ret = list(filter(lambda day: get_difference(day[0]) < 15, year))
    return ret


def get_difference(day: datetime) -> int:
    ret = abs((day - now).days)
    return ret


def historical_past_two_weeks(years: List[List[Tuple[datetime, float]]]) -> float:
    averages = []
    for year in years:
        year = np.transpose(year)
        trimmed = trim_to_two_weeks(year)
        if len(trimmed) == 0:
            continue
        avg = get_average(trimmed)
        averages.append(avg)
    return mean(averages)


def rough_date() -> str:
    month = now.strftime("%B")
    prefix = "early " if now.day < 10 else "mid-" if now.day < 20 else "late "
    return prefix + month
