import pandas as pd
import geopy.distance
import numpy as np
from utils.data_process import read_csv


def get_distances_with_df(df1, df2, df1_basis, df2_basis):
    rows = []
    for j in range(df1.shape[0]):
        loc_name1 = df1.loc[j][df1_basis]
        coord1 = (df1.loc[j].latitude, df1.loc[j].longitude)
        for i in range(df2.shape[0]):
            try:
                loc_name2 = df2.loc[i][df2_basis]
                coord2 = (df2.loc[i].latitude, df2.loc[i].longitude)
                distance = geopy.distance.vincenty(coord1, coord2).km
                row = {
                    df1_basis: loc_name1,
                    df2_basis: loc_name2,
                    'distance': distance
                }
            except Exception as e:
                print(e, df2.loc[i][df2_basis])
                row = {
                    df1_basis: loc_name1,
                    df2_basis: loc_name2,
                    'distance': 9999
                }
            rows.append(row)
    return rows


def find_min_dist_starbucks(groupped_df, basis_name='star_name', min_numbers=2):
    new_df = {}
    groupped_df = groupped_df.sort_values(by='distance').reset_index(drop=True)
    new_df['distance'] = groupped_df.loc[:min_numbers]['distance']
    new_df[basis_name] = groupped_df.loc[:min_numbers][basis_name]
    if min_numbers > 1:
        print('this df contains column which has multiple list, please use [column_list_to_multiple_rows] function.')
    return pd.Series(new_df, index=[basis_name, 'distance'])


def column_list_to_multiple_rows(df, base_column: str, multi_column_names: list):
    df_dict = {base_column: np.repeat(df[base_column].values, df[multi_column_names[0]].str.len())}
    for column_name in multi_column_names:
        df_dict[column_name] = np.concatenate(df[column_name].values)
    return pd.DataFrame(df_dict)


def example_mac_star_dist_cal():
    loc_info = pd.read_csv('../data/mac/ST_MAC2_DT.csv', sep='\t')
    loc_info_mac = loc_info[loc_info.SORT == '맥도날드']
    loc_info_star = loc_info[loc_info.SORT == '스타벅스']
    loc_info_star = loc_info_star.reset_index().drop('index', axis=1)

    loc_info_mac = loc_info_mac.drop_duplicates().reset_index(drop=True)

    rows = get_distances_with_df(loc_info_mac, loc_info_star, df1_basis='mac_name', df2_basis='mac_name')
    mac_star_distance = pd.DataFrame(rows)
    mac_star_distance2 = mac_star_distance.groupby(['mac_name']).apply(
        lambda x: find_min_dist_starbucks(x, 'mac_name', 1))
    mac_star_distance3 = mac_star_distance2.reset_index()
    mac_star_distance3.to_csv('data/mac_star_distance.csv', sep='\t')


def distance_calculate(source_df, target_df, save_name, distance_number=1):
    """
    :param source_df: ex) ['loc_name', 'latitude', 'longitude']
    :param target_df: ex) ['기업명', 'latitude', 'longitude']
    :param save_name:
    :param distance_number:
    :return:
    """
    source_basis = source_df.columns[0]
    target_basis = target_df.columns[0]
    rows = get_distances_with_df(df1=source_df, df2=target_df, df1_basis=source_basis, df2_basis=target_basis)
    src_tar_distance = pd.DataFrame(rows)
    src_tar_distance2 = src_tar_distance.groupby([source_basis]).apply(
        lambda x: find_min_dist_starbucks(x, source_basis, distance_number))
    if distance_number > 1:
        src_tar_distance2 = column_list_to_multiple_rows(src_tar_distance2, source_basis, [target_basis, 'distance'])
    src_tar_distance2 = src_tar_distance2.reset_index()
    src_tar_distance2.to_csv(f'data/{save_name}_distance.csv', sep='\t')


def main_startbucks_tourist():
    travel_data_path = 'data/new_2020-07-02_18_46_travel_crawl.csv'
    travel_data = read_csv(travel_data_path)
    starbucks_data_path = '../company_list/starbucksDT_location_info_20200703.csv'
    starbucks_data = read_csv(starbucks_data_path)
    distance_calculate(starbucks_data, travel_data, 'Starbucks_btw_Tourist', distance_number=2)


def main_startbucks_apt():
    apt_data_path = '/Users/dhkim/PycharmProjects/kakomap_crwal/data/2020-07-02_18_46_travel_crawl.csv'
    apt_data = pd.read_csv(apt_data_path, sep='\t')
    starbucks_data_path = '/Users/dhkim/PycharmProjects/company_list/starbucks_location_info.csv'
    starbucks_data = pd.read_csv(starbucks_data_path, sep='\t')
    distance_calculate(starbucks_data, apt_data, 'Starbucks_btw_Apt', distance_number=1)


if __name__ == '__main__':
    import os
    os.chdir('..')
    main_startbucks_tourist()