import pandas as pd
import sys
import time

cols = ["action", "file", "enum", "lxml_path", "parsed_cite", "text"]


def compare_dfs(df_1, df_2):
    df_1 = df_1[cols].copy()
    df_2 = df_2[cols].copy()
    for col in cols:
        df_1[col] = df_1[col].apply(lambda x: str(x).strip())
        df_2[col] = df_2[col].apply(lambda x: str(x).strip())

    merged = df_1.merge(
        df_2, on=["lxml_path"], right_index=True, how="inner", suffixes=("_old", "_new")
    )
    for col in ["action", "parsed_cite"]:
        merged[f"{col}_new"] = merged[f"{col}_new"].apply(lambda x: str(x).strip())
        merged[f"{col}_old"] = merged[f"{col}_old"].apply(lambda x: str(x).strip())
    merged["changes"] = (merged["action_old"] != merged["action_new"]) | (
        merged["parsed_cite_old"] != merged["parsed_cite_new"]
    )
    merged = merged[merged["changes"]]
    merged = merged[
        [
            "file_old",
            "enum_old",
            "enum_new",
            "lxml_path",
            "text_new",
            "action_old",
            "action_new",
            "parsed_cite_old",
            "parsed_cite_new",
        ]
    ]
    merged.to_csv(
        "reports/compare_{}.csv".format(time.strftime("%d-%m-%Y_%H-%M")), index=False
    )


if __name__ == "__main__":
    df_1 = pd.read_csv(sys.argv[1])
    df_2 = pd.read_csv(sys.argv[2])
    compare_dfs(df_1, df_2)
