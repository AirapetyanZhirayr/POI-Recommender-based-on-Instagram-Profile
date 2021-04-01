import pandas as pd
import numpy as np
from collections import defaultdict

def preprocess_data(dfPath):
    '''
    This function indexes user_names and POIs
    And builds dataset for TransRec Algo
    :param dfPath: path of csv file consisting data
    :return: data[user_id] = [(POI, timestamp) for all user POIs]
             user2id: dictionary of user ids
             id2user: list that maps user_id to user_name
             poi2id: dictionary of POI ids
             id2poi: list that maps POI ids to POI names
    '''

    df = pd.read_csv(dfPath)

    user2id = {}
    id2user = []
    poi2id = {}
    id2poi = []
    data = defaultdict(list)

    for index, row in df.iterrows():
        user = row['user']
        poi= row['location']
        timestamp = row['timestamp']
        if poi is np.nan: continue
        if user not in user2id:
            user2id[user] = len(user2id)
            id2user.append(user)
        if poi not in poi2id:
            poi2id[poi] = len(poi2id)
            id2poi.append(poi)
        data[user2id[user]].append((poi2id[poi], timestamp))

    return data, id2user, user2id, id2poi, poi2id

def delete_consecutive_duplicates(list):
    '''
    Builds a new_list without consecutive duplicates in given list
    :return: new_list
    '''
    new_list = []
    for i in range(len(list)):
        next_el = list[i]
        if i == 0:
            new_list.append(next_el)
            continue
        prev_el = new_list[-1]
        if prev_el!=next_el:
            new_list.append(next_el)
    return new_list

def train_test_split(data):
    '''
    Performs train-test split for TransRec Algo.
    Last consecutive POI pare goes to test, others go to train.
    :param data: dict of type data[user_id] = [(POI, timestamp) for all user POIs]
    :return: train_data: train_data[user_id] = [(previous_POI, next_POI)
                                    for all consecutive POI pairs of user except the last one]
             test_data: test_data[user_id] = (previous_POI, next_POI) for the last two consecutive
                                            visited  POIs
            train_POIs: dict with user POIs from train set
    '''
    train_data = defaultdict(list)
    test_data = defaultdict(list)
    train_POIs = defaultdict(set)
    for user_id in data:
        data[user_id] = delete_consecutive_duplicates(              # deleting consec. duplicates after sorting
                        list(map(lambda x: x[0],                    # droping timestamp after sorting
                        sorted(data[user_id], key=lambda x: x[1])   # sorting by timestamp
                                 )))

        for i in range(1, len(data[user_id])):
            prev_poi = data[user_id][i-1]
            next_poi = data[user_id][i]
            if i == (len(data[user_id]) - 1):
                test_data[user_id].append((prev_poi, next_poi))
            else:
                train_data[user_id].append((prev_poi, next_poi))
                train_POIs[user_id].add(prev_poi)
                train_POIs[user_id].add(next_poi)

    return train_data, test_data, train_POIs

def get_batches(train_data, train_POIs, batch_size, num_sampled, n_poi):
    '''
    This function performs batch spliting for training
    :param data: dict of type train_data[user] = [(previous_POI, next_POI)
                                         for all  consecutive POI pairs of user except last one]]
    :param train_POIs: dict with user POIs from train set
    :param num_sampled: number of negative examples for each positive example
    :param n_poi: overall number of available POIs
    '''

    _data = []
    for user in train_data:
        for (prev_poi, pos_poi) in train_data[user]:
            negative_samples = set(np.random.randint(0, n_poi, num_sampled)) - train_POIs[user]
            for neg_poi in negative_samples:
                _data.append((user, prev_poi, pos_poi, neg_poi))

    np.random.shuffle(_data)
    batch_num = len(_data)//batch_size + int(len(_data)%batch_size != 0)
    for i in range(batch_num):
        left = i * batch_size
        right = min(len(_data), (i + 1) * batch_size)
        user, prev, pos, neg = [],[],[],[]
        for line in _data[left:right]:
            user.append(line[0])
            prev.append(line[1])
            pos.append(line[2])
            neg.append(line[3])

        yield user, prev, pos, neg




