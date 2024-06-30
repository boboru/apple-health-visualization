import argparse
from datetime import datetime

import numpy as np
import pandas as pd
from faker import Faker


def simulate(start_date=datetime(2024, 1, 1), end_date=datetime.now()):
    fake = Faker()
    rng = np.random.default_rng()

    sleep_stages = [
        "HKCategoryValueSleepAnalysisInBed",
        "HKCategoryValueSleepAnalysisAsleepCore",
        "HKCategoryValueSleepAnalysisAsleepREM",
        "HKCategoryValueSleepAnalysisAsleepDeep",
        "HKCategoryValueSleepAnalysisAwake",
    ]

    date_range = end_date - start_date
    n_day = date_range.days
    date_starts = []
    durations = []
    values = []
    type_ = []
    # sleep
    for stage in sleep_stages:
        # decide # days
        if stage == "HKCategoryValueSleepAnalysisInBed":
            cnt_base = 3
            duration_base = 8
        else:
            cnt_base = 6
            duration_base = 1

        # how many records
        cnt = rng.integers(low=0, high=cnt_base * n_day)
        date_start_temp = [
            fake.date_time_between_dates(
                datetime_start=start_date, datetime_end=end_date
            )
            for _ in range(cnt)
        ]
        date_starts.extend(date_start_temp)

        # duration
        durations_temp = rng.integers(
            low=30 * 60, high=duration_base * 60 * 60, size=cnt
        ).tolist()
        durations.extend(durations_temp)

        values.extend([stage] * cnt)

    type_.extend(["HKCategoryTypeIdentifierSleepAnalysis"] * len(values))

    # heart rate
    cnt = rng.integers(low=0, high=50 * n_day)
    date_start_temp = [
        fake.date_time_between_dates(datetime_start=start_date, datetime_end=end_date)
        for _ in range(cnt)
    ]
    date_starts.extend(date_start_temp)
    values.extend(rng.integers(low=90, high=130, size=cnt).tolist())  # BPM: 90 ~ 130
    durations.extend([0] * cnt)
    type_.extend(["HKQuantityTypeIdentifierHeartRate"] * cnt)

    df = pd.DataFrame(
        {
            "type": type_,
            "startDate": date_starts,
            "durations": durations,
            "value": values,
        }
    )

    df["durations"] = pd.to_timedelta(df["durations"], unit="s")
    df["endDate"] = df["startDate"] + df["durations"]
    df["sourceName"] = ""
    df["unit"] = ""
    df = df[["type", "sourceName", "unit", "startDate", "endDate", "value"]]
    df["startDate"] = df["startDate"] 
    df["endDate"] = df["endDate"]
    df["value"] = df["value"].astype(str)
    df.to_feather("./data/test.feather")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate fake data.")
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="path to exported feather file",
    )
    args = parser.parse_args()

    df = simulate()
    if args.file is not None:
        df.to_feather(args.file)
