import requests
from utils.csv_postprocess import postprocess_df

def find_lat_lng(location):
    # 요청 주소(구글맵)

    # Production(실제 서비스) 환경 - https 요청이 필수이고, API Key 발급(사용설정) 및 과금 설정이 반드시 필요합니다.
    URL = 'https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyBWgPcQF1nWKXIwGLPJVZA4-QYLw5GdVVM' \
          '&sensor=false&language=ko&address={}'.format(location)
    try:
        # URL로 보낸 Requst의 Response를 response 변수에 할당
        response = requests.get(URL)

        # JSON 파싱
        data = response.json()

        # lat, lon 추출
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']
    except:
        print('time exceed')
        find_lat_lng(location)
    #         lat, lng = 0, 0
    return lat, lng

def dataframe_loc_convert(df, address_column):
    if isinstance(df, str):
        save_path = df
        import pandas as pd
        df = pd.read_csv(save_path, sep='\t')
    else:
        save_path = 'data/converted_result.csv'

    df['latitude'] = ""
    df['longitude'] = ""

    locs = []
    for i, loc in enumerate(df[address_column]):
        lat, lng = find_lat_lng(loc)
        df['latitude'].iloc[i] = lat
        df['longitude'].iloc[i] = lng
        print(f"{lat}'\t'{lng}")
        locs.append((lat, lng))

    if "Unnamed: 0" in df.columns:
        df = df.drop("Unnamed: 0", axis=1)
    df.to_csv(save_path, sep='\t')
    return save_path

if __name__ == '__main__':
    file_path = 'data/2020-06-24_15_25_맥드라이브.csv'
    dataframe_loc_convert(file_path, 'address')
    postprocess_df(file_path)