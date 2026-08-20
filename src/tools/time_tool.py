import needle
import datetime


@needle.tool
def get_time_tool():
    "Get the current date and time on this machine."

    now = datetime.datetime.now()

    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": now.strftime("%A"),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "__labels__": {
            "date": "Date",
            "time": "Time",
            "datetime": "Date & Time",
            "weekday": "Day of Week",
            "year": "Year",
            "month": "Month",
            "day": "Day",
            "hour": "Hour",
            "minute": "Minute",
            "second": "Second",
        },
    }
