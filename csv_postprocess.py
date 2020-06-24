import requests
import pprint
import pandas as pd
import os


def postprocess_df(file_path):
    df = pd.read_csv(file_path, sep='\t')
    for col in df.columns:
        if "Unnamed" in col:
            df = df.drop(col, axis=1)
    _dir = os.path.dirname(file_path)
    _path = file_path.split(os.path.sep)[-1]
    new_path = os.path.join(_dir, 'new2_' + _path)

    print(df[df.duplicated(['mac_name'])])
    df = df.drop_duplicates(['mac_name']).reset_index(drop=True)
    # df = df.drop_duplicates(['latitude', 'longitude']).reset_index(drop=True)
    df.to_csv(new_path, sep='\t')


if __name__ == '__main__':
    file_path = 'data/2020-06-24_16_53_맥드라이브.csv'
    postprocess_df(file_path)