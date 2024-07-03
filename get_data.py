import requests as rq


def get_data() -> str:
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

    try:
        with open("data.csv") as data:
            response = str(data.read())
    except:
        response: str = rq.get(
            url="https://aqrt.nrs.gov.bc.ca/Export/DataSet", params=params
        ).text
        with open("data.csv", "w") as data:
            data.write(response)
    return "\n".join(response.splitlines()[6:])
