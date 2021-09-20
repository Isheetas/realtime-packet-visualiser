'''
Used to plot the logs, given the log file name
'''
import numpy as np
import pdb
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

plot_key = {}
index = -1
pps = []
mbps = []
loss = []
jitter = []


def plot_log(filename):

    global index
    global plot_key, pps, mbps, loss, jitter

    file = open(filename, 'r')
    lines = file.read().splitlines()


    media = {}



    for line in lines:
        if (len(line.split('DEBUG:root:Log: ')) < 2):
            continue
        log_str = line.split('DEBUG:root:Log: ')[1]
        log_obj = json.loads(log_str)

        data = log_obj['sent']
        

        for key in data:
            info = data[key]['info']
            if (info['protocol'] != 'UDP'):
                continue

            update_plot_key(key)
            i = plot_key[key]

            #print(key, index)

            media[key] = data[key]['data']['media']

            pps[i].append(data[key]['data']['pps'])
            mbps[i].append(data[key]['data']['mbps'])
            #plen[i].append(data[key]['data']['len'])
            loss[i].append(data[key]['data']['loss'])
            jitter[i].append(data[key]['data']['jitter'])


    
    fig = make_subplots(rows=4, cols=1, subplot_titles=('PPS', 'MBPS', 'LOSS', 'JITTER'))

    fig.add_trace(go.Scatter(y=pps[0], mode='lines', name=f'key1', line=dict(color='red')), row=1, col=1)
    fig.add_trace(go.Scatter(y=pps[1], mode='lines', name=f'key2', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(y=pps[2], mode='lines', name=f'key3', line=dict(color='green')), row=1, col=1)


    #fig.add_trace(go.Scatter(y=plen[0], mode='lines', name=f'key1'), row=2, col=1)
    #fig.add_trace(go.Scatter(y=plen[1], mode='lines', name=f'key2'), row=2, col=1)
    #fig.add_trace(go.Scatter(y=plen[2], mode='lines', name=f'key3'), row=2, col=1)

    fig.add_trace(go.Scatter(y=mbps[0], mode='lines', name=f'key1', line=dict(color='red')), row=2, col=1)
    fig.add_trace(go.Scatter(y=mbps[1], mode='lines', name=f'key2', line=dict(color='blue')), row=2, col=1)
    fig.add_trace(go.Scatter(y=mbps[2], mode='lines', name=f'key3', line=dict(color='green')), row=2, col=1)

    fig.add_trace(go.Scatter(y=loss[0], mode='lines', name=f'key1', line=dict(color='red')), row=3, col=1)
    fig.add_trace(go.Scatter(y=loss[1], mode='lines', name=f'key2', line=dict(color='blue')), row=3, col=1)
    fig.add_trace(go.Scatter(y=loss[2], mode='lines', name=f'key3', line=dict(color='green')), row=3, col=1)

    fig.add_trace(go.Scatter(y=jitter[0], mode='lines', name=f'key1', line=dict(color='red')), row=4, col=1)
    fig.add_trace(go.Scatter(y=jitter[1], mode='lines', name=f'key2', line=dict(color='blue')), row=4, col=1)
    fig.add_trace(go.Scatter(y=jitter[2], mode='lines', name=f'key3', line=dict(color='green')), row=4, col=1)

    print(media)

    fig.show()

def update_plot_key(key):

    
    global index
    global plot_key, pps, mbps, loss, jitter
    
    if (key not in plot_key):
        #print(key, index, plot_key)
        plot_key[key] = index +1
        index = index+1
        pps.append([])
        loss.append([])
        jitter.append([])
        mbps.append([])



if __name__ == "__main__":
    plot_log('logs/2021_09_05_19_05_56.log')
    