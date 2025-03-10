import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class JointModel(nn.Module):
    def __init__(self, question_num, max_choices, encoder_layers_num, attention_heads, hidden_dim, dropout=0.1):
        super().__init__()
        self.question_num = question_num
        self.max_choices = max_choices
        self.encoder_layers_num = encoder_layers_num
        self.encoder = Encoder(question_num, max_choices, self.encoder_layers_num, attention_heads, dropout)
        self.fc = nn.Sequential(
            nn.Linear(question_num * max_choices * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, max_choices-1)
        )
        

    def first_layer_embedding(self, x): # hand coded embedding of llm's response in distribution form
        return x

    def forward(self, x):
        x = self.first_layer_embedding(x)
        x = self.encoder(x)
        x = x.view(x.shape[0], -1)
        x = self.fc(x)
        x = F.softmax(x, dim=-1)
        return x

class Encoder(nn.Module):
    def __init__(self, question_num, max_choices, encoder_num, attention_heads, dropout=0.1):
        super().__init__()
        self.position_encoder = Positional_Encoder(question_num, max_choices)
        self.layers = nn.ModuleList([EncoderLayer(max_choices * 2, attention_heads, dropout) for _ in range(encoder_num)])
        self.norm = NormLayer(max_choices * 2)

    def forward(self, x):
        x = self.position_encoder(x)
        for index, layer in enumerate(self.layers):
            if index == 0:
                x = layer(x, False)
            else:
                x = layer(x, True)
        return self.norm(x)


    
class EncoderLayer(nn.Module):
    def __init__(self, d_model, attention_heads, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.attention_heads = attention_heads
        self.Q = nn.Linear(d_model, d_model)
        self.K = nn.Linear(d_model, d_model) #maybe can change this to have embeddings have different dimensions
        self.V = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)
        self.out = nn.Linear(d_model, d_model)
        self.norm_1 = NormLayer(d_model)
        self.norm_2 = NormLayer(d_model)
        self.dropout_1 = nn.Dropout(dropout)
        self.dropout_2 = nn.Dropout(dropout)
        self.ff = FeedForward(d_model, dropout=dropout)

    def multihead_attention(self, x, batch_size):
        Q = self.Q(x).view(batch_size, -1, self.attention_heads, self.d_model // self.attention_heads).transpose(1, 2)
        K = self.K(x).view(batch_size, -1, self.attention_heads, self.d_model // self.attention_heads).transpose(1, 2)
        V = self.V(x).view(batch_size, -1, self.attention_heads, self.d_model // self.attention_heads).transpose(1, 2)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_model // self.attention_heads)
        scores = F.softmax(scores, dim=-1)
        scores = self.dropout(scores)
        scores = torch.matmul(scores, V)
        scores = scores.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.out(scores)
        return output
    

    def forward(self, x, normalization=True):
        batch_size = x.shape[0]
        if normalization:
            x = self.norm_1(x)
        x = x + self.dropout_1(self.multihead_attention(x, batch_size))
        x = self.norm_2(x)
        x = x + self.dropout_2(self.ff(x))
        return x
        

class Positional_Encoder(nn.Module):
    def __init__(self, question_num, max_choices):
        super().__init__()
        self.question_num = question_num
        self.max_choices = max_choices
    
    def position_encoding(self, x):
        positional_embedding = torch.zeros(self.question_num, self.max_choices)
        for pos in range(self.question_num):
            for i in range(0, self.max_choices, 2):
                positional_embedding[pos, i] = math.sin(pos / (10000**((2 * i) / self.max_choices)))
                if i + 1 < x.shape[2]:
                    positional_embedding[pos, i+1] = math.cos(pos / (10000**((2 * (i + 1)) / self.max_choices)))
        return positional_embedding

    def forward(self, x):
        pe = self.position_encoding(x)
        pe = pe.unsqueeze(0).expand(x.shape[0], -1, -1)
        x = torch.cat((pe, x), dim=-1)
        return x

class NormLayer(nn.Module):

    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.size = d_model
        self.alpha = nn.Parameter(torch.ones(self.size))
        self.bias = nn.Parameter(torch.zeros(self.size))
        self.eps = eps

    def forward(self, x):
        norm = self.alpha * (x - x.mean(dim=-1, keepdim=True)) \
        / (x.std(dim=-1, keepdim=True) + self.eps) + self.bias
        return norm

class FeedForward(nn.Module):

    def __init__(self, d_model, d_ff=2048, dropout=0.1):
        super().__init__()
        self.linear_1 = nn.Linear(d_model, d_ff)
        self.dropout = nn.Dropout(dropout)
        self.linear_2 = nn.Linear(d_ff, d_model)

    def forward(self, x):
        x = self.dropout(F.relu(self.linear_1(x)))
        x = self.linear_2(x)
        return x



