from instabot import InstaScrapper
from preprocessing_data import build_csv, extract_city_country
api_key = 'AIzaSyBxUfr9s7gZqUdJZouWS6AmgXeoyFPppqk'
from tqdm import tqdm
import requests
import numpy as np
import json

import torch, torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

with open('data/login.txt', 'r') as f:
    log_pass = []
    for line in f:
        log_pass.append(line.split('\n')[0])
    login, password = log_pass

scrapper = InstaScrapper(login, password, testing=True)
scrapper.login()

poi_num = 1506
EMBEDDING_DIM = 300
LSTM_NUM_UNITS = 512

with open('data/poi2id.json') as f:
    poi2id = json.load(f)
with open('data/id2poi.json') as f:
    id2poi = json.load(f)


def indexing(_context):
    context = [poi2id.get(poi, 0) for poi in _context]
    return context


def as_matrix(sequences, max_len=None):
    max_len = max_len or max(map(len, sequences))
    matrix = np.zeros((len(sequences), max_len), dtype=np.int32)
    for i, seq in enumerate(sequences):
        matrix[i, :len(seq)] = seq
    return matrix


class LSTMLoop(nn.Module):
    def __init__(self, poi_num, embedding_dim, lstm_num_units, embedding_matrix):
        super().__init__()
        self.poi_num = poi_num
        self.embedding_dim = embedding_dim
        self.lstm_num_units = lstm_num_units
        self.weight = Variable(torch.FloatTensor(embedding_matrix))

        self.emb = nn.Embedding(self.poi_num, self.embedding_dim, _weight=self.weight)
        self.lstm = nn.LSTM(self.embedding_dim, self.lstm_num_units, batch_first=True)
        self.logits = nn.Linear(self.lstm_num_units, self.poi_num)

        self.emb.weight.requires_grad = False

    def forward(self, context):
        lstm_inp = self.emb(context)
        lstm_out, _ = self.lstm(lstm_inp)
        logits = self.logits(lstm_out)
        return logits
    
def predict_word(network, seq, k=1, different=False):
    network.train(False)
    previous_word = Variable(torch.LongTensor(as_matrix([seq])))
    next_word_logits = network.forward(previous_word)[0, -1]
    next_word_probs = F.softmax(next_word_logits, -1).detach().numpy()
    next_word_ix = np.argsort(next_word_probs)[::-1]
    if different:
        for i in seq:
            next_word_ix = np.delete(next_word_ix, np.where(next_word_ix == i)[0])
    if k == 'all':
        return next_word_ix
    return next_word_ix[:k]
    
EMBEDDING_MATRIX = np.loadtxt('data/emb_mat.txt')
network = LSTMLoop(poi_num, EMBEDDING_DIM, LSTM_NUM_UNITS, EMBEDDING_MATRIX)
network.load_state_dict(torch.load('data/lstm_weight.pt'))


def predict_user(username):
    '''
    Predicting locations straight from user
    instagram page
    '''
    user_data = scrapper.collect_user_data(username)
    if user_data:
        user_df = build_csv(user_data, testing=True)
        user_data = []
        for idx, row in user_df.iterrows():
            user_data.append((row['location'], row['timestamp']))
        user_data = list(map(lambda y: y[0], sorted(user_data, key=lambda x: x[1])))

        user_data_processed = []
        for loc in (user_data):
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={loc}&key={api_key}"
            request = requests.get(url).json()
            if request['status'] == 'OK':
                result = request['results']
                if result:
                    result = result[0]
                    _loc = extract_city_country(result['address_components'])
                    city = _loc['city']
                    country = _loc['country']

                    user_data_processed.append(city + ', ' + country)

        user_data_processed = indexing(user_data_processed)
        predict_labels = predict_word(network, user_data_processed, 5, different=True)
        return [id2poi[label] for label in predict_labels]

    else:
        return None



    