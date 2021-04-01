from myTransRec import TransRec
from utils import train_test_split, preprocess_data, get_batches
from torch import nn
import torch.optim as optim
import torch


EMBEDDING_DIM = 100
LEARNING_RATE = 0.001
EPOCHS = 20000
BATCH_SIZE = 1024
LAMBDA = 0.05
NUM_SAMPLED = 16
dfPath = '/Users/jiji/RS_project/df_cutted.csv'
data, user2id, id2user, poi2id, id2poi = preprocess_data(dfPath)
n_users = len(id2user); n_poi = len(id2poi)

train_data, test_data = train_test_split(data)

model = TransRec(EMBEDDING_DIM, n_users, n_poi)
criterion = nn.LogSigmoid()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=LAMBDA)

for i in range(EPOCHS):

    batches = get_batches(train_data, BATCH_SIZE, NUM_SAMPLED, model.n_poi)
    step = 0
    batch_num = int(len(train_data)/BATCH_SIZE) + 1
    loss = .0
    for batch in batches:
        user_id, prev_id, pos_id, neg_id = map(torch.LongTensor, batch)
        optimizer.zero_grad()
        objective = model(user_id, prev_id, pos_id, neg_id)
        _loss = - criterion(objective).sum()
        _loss.backward()
        optimizer.step()
        loss+=_loss.data.numpy()[0]

        step+=1
        print("Epoch: [{}/{}] Batch: [{}/{}]".format(i+1, EPOCHS, step, batch_num))



