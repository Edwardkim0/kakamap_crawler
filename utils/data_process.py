import os
from datetime import datetime

def save_dataframe(search_name, df):
    now = datetime.now()
    save_dir = 'data'
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, now.strftime("%Y-%m-%d_%H_%M_") + search_name + '.csv')
    df.to_csv(save_path, sep='\t')
    return save_path