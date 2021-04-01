import numpy as np
import pandas as pd

# dfPath = '/Users/jiji/RS_project/df_cutted.csv'
# df = pd.read_csv(dfPath)
#
# data = []
# user2id = {'<PAD>':0}
# id2user = ['<PAD>']
# item2id = {'<PAD>':0}
# id2item = ['<PAD>']
#
# n_users = df['user'].unique()
# n_items = df['location'].unique() - int(np.nan in list(df['location'].unique()))
# data = [[] for i in range(n_users+1)]
# for index, row in df.iterrows():
#     user = row['user']
#     item = row['location']
#     timestamp = row['timestamp']
#     source = row['source']
#     subscription = row['subscription']
#     if user not in user2id:
#         user2id[user] = len(user2id)
#         id2user.append(user)
#     if item not in item2id:
#         item2id[item] = len(item2id)
#         id2item.append(item)
#     data[user2id[user]].append((item2id[item], timestamp))
#
# train_data = []
# test_data = []
# for i in range(len(data)):
#     data[i] = list(map(lambda x: x[0], sorted(data[i], lambda x: x[1])))
#     for j in range(1, len(data[i])):
#         current = data[i][j-1]
#         next = data[i][j]
#         if j == len(data[i])-1:
#             test_data.append((current, next))
#         else:
#             train_data.append((current, next))



