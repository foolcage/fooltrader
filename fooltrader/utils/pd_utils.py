# -*- coding: utf-8 -*-
import pandas as pd


def kdata_df_save(df, to_path):
    df = df.drop_duplicates(subset='timestamp', keep='last')
    df = df.set_index(df['timestamp'], drop=False)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.to_csv(to_path, index=False)
