import pandas as pd
import geopy.distance


def get_distances_with_st(mac_df, star_df):
    rows = []
    for j in range(mac_df.shape[0]):
        mac_name = mac_df.loc[j].mac_name
        coord1 = (mac_df.loc[j].latitude, mac_df.loc[j].longitude)
        for i in range(star_df.shape[0]):
            star_name = star_df.loc[i].mac_name
            coord2 = (star_df.loc[i].latitude, star_df.loc[i].longitude)
            distance = geopy.distance.vincenty(coord1, coord2).km
            row = {
                'mac_name': mac_name,
                'star_name': star_name,
                'distance': distance
            }
            rows.append(row)
    return rows


def find_mindist_starbucks(each_mac_df):
    new_df = {}
    each_mac_df = each_mac_df.reset_index(drop=True)
    new_df['distance'] = each_mac_df['distance'].min()
    new_df['star_name'] = each_mac_df.loc[each_mac_df['distance'].argmin()]['star_name']

    return pd.Series(new_df, index=['star_name', 'distance'])


def main():
    loc_info = pd.read_csv('../data/mac/ST_MAC2_DT.csv', sep='\t')
    loc_info_mac = loc_info[loc_info.SORT == '맥도날드']
    loc_info_star = loc_info[loc_info.SORT == '스타벅스']
    loc_info_star = loc_info_star.reset_index().drop('index', axis=1)

    loc_info_mac = loc_info_mac.drop_duplicates().reset_index(drop=True)

    rows = get_distances_with_st(loc_info_mac, loc_info_star)
    mac_star_distance = pd.DataFrame(rows)
    mac_star_distance2 = mac_star_distance.groupby(['mac_name']).apply(find_mindist_starbucks)
    mac_star_distance3 = mac_star_distance2.reset_index()
    mac_star_distance3.to_csv('data/mac_star_distance.csv', sep='\t')

if __name__ == '__main__':
    main()