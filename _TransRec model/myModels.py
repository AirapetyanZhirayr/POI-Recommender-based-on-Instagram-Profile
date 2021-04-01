import torch
from torch import nn

class mySPAN(nn.Module):

    def __init__(self, t_dim, l_dim, u_dim, embed_dim, ex, dropout=0.1):
        super(Model, self).__init__()
        emb_t = nn.Embeding(t_dim, embed_dim, padding_idx=0)
        emb_l = nn.Embeding(l_dim, embed_dim, padding_idx=0)
        emb_u = nn.Embeding(u_dim, embed_dim, padding_idx=0)

        emb_su = nn.Embeding(2, embed_dim, padding_idx=0)
        emb_sl = nn.Embeding(2, embed_dim, padding_idx=0)
        emb_su = nn.Embeding(2, embed_dim, padding_idx=0)
        emb_tu = nn.Embeding(2, embed_dim, padding_idx=0)
        emb_tl = nn.Embeding(2, embed_dim, padding_idx=0)
        embed_layers = (emb_t, emb_l, emb_u, emb_su, emb_sl, emb_tu, emb_tl)
        



