from scapy.all import *
import statistics
from datetime import datetime
import logging 
import json

import numpy as np

class ProcessPacket:
    def __init__(self):
        self.data = {}
        self.flows = {}                     # all flow information is stored for each second
        self.flow_key = 0
        self.state = {
            'audio': False,
            'video': False,
            'content': False,
        }

    # receive packet for processing
    def process_packet(self, packet):

        flow_key = self.get_flow(packet) 

        self.set_packet_len(flow_key, packet)
        self.set_pps(flow_key, packet)
        if (packet.haslayer(UDP)):
            self.set_jitter(flow_key, packet)
            self.set_packet_loss(flow_key, packet)

        

    def post_process(self):
        return


    # return the flow (object) for that packet (if a new flow, creates an )
    def get_flow(self, packet):
        srcip = ''
        dstip = ''
        srcport = 0
        dstport = 0
        protocol = ''

        if (TCP in packet):
            srcip = packet[IP].src
            dstip = packet[IP].dst
            protocol = 'TCP'

    
        if (UDP in packet):
            srcport = packet[UDP].sport
            dstport = packet[UDP].dport
            srcip = packet[IP].src
            dstip = packet[IP].dst
            protocol = 'UDP'

        # header information of the flow
        info = {
            'srcip': srcip,
            'srcport': srcport,
            'dstip': dstip,
            'dstport': dstport,
            'protocol': protocol
        }

        
        # if flow not in existent, then creates a new object for that flow - with relevant fiel --> loss, packet len info, media, pps, mbps
        if (info not in self.flows.values()):
            self.flows[self.flow_key] = info
            loss = {
                'count': 0,
                'expectedSeq': -1,
                'total': 0,
                'percentage': 0,
                
            }
            len_obj = {
                'arr': [],
                'avg' : 0,
                'std' : 0,
                'arr_5' : [],
                'max_len': 0,
                'avg_5': 0,
            }

            media = {
                'media': 'inactive',
                'state': '',
                'audio': 0,
                'video': 0,
                'content': 0,
                'unknown': 0,
            }

            pps = {
                'count': 0,
                'pps_avg': 0,
                'pps_arr': [],
                'std': 0,
                'max_pps': 0,
            }

            mbps = {
                'mbps_arr': [],
                'count': 0,
                'avg': 0,
            }



            if (info['protocol'] == 'UDP'):
                self.data[self.flow_key] = {
                        'pps': pps, 
                        'jitter': {'prev_time': 0, 'all_delay': [], 'avg':0}, 
                        'loss': loss, 
                        'media':media,
                        'len': len_obj,
                        'active': False,
                        'mbps': mbps,
                    }           
            if (info['protocol'] == 'TCP'):
                self.data[self.flow_key] = {'pps': pps,'len': len_obj, 'mbps': mbps,}

            self.state[dstport] = False
            self.flow_key += 1

        key = list(self.flows.keys())
        val = list(self.flows.values())
        pos = val.index(info)
        return key[pos]

    def set_pps(self, key, packet):
        info = self.flows[key]
        self.data[key]['pps']['count'] += 1
        self.data[key]['mbps']['count'] =  self.data[key]['mbps']['count'] + packet.getlayer(IP).len
        return
    
    def set_jitter(self, key, packet):
        jitter_data = self.data[key]['jitter']
        if (jitter_data['prev_time'] == 0):
            jitter_data['prev_time'] = packet.time
        else:
            delay = int ((packet.time - jitter_data['prev_time']) * 1000)
            jitter_data['all_delay'].append(delay)
            jitter_data['prev_time'] = packet.time
            if (len(jitter_data['all_delay']) > 2):
                stdev = statistics.stdev(jitter_data['all_delay'])
                jitter_data['avg'] = stdev

    def set_packet_loss(self, key, packet):
        seq = self.get_seq(packet)
        loss = self.data[key]['loss']
        loss['total'] += 1

        if (seq == -1):
            return

 
        if (loss["expectedSeq"] == -1):
            loss['expectedSeq'] = seq + 1
            return
     

        if (seq == loss['expectedSeq']):
            loss['expectedSeq'] += 1

        else:
            while (loss['expectedSeq'] != seq):
                loss['count'] += 1
                loss['expectedSeq'] += 1 


            loss['expectedSeq'] += 1 





        

    def get_seq(self, packet):
        seq = -1
        byte = packet.getlayer(Raw).load
        if (byte[0] == 5):
            val = byte[1:3]
            seq = int.from_bytes(val, "big")
        return seq

    def set_packet_len(self, key, packet):
        len_info = self.data[key]['len']
        len_info['arr'].append(packet.getlayer(IP).len)
        port = self.flows[key]['dstport']
        len_ = len(len_info['arr'])

        if (packet.getlayer(IP).len > len_info['max_len']):
            len_info['max_len'] = packet.getlayer(IP).len

    def set_packet_len_avg(self, key):
        len_info = self.data[key]['len']
        if (len(len_info['arr']) > 0):
            len_info['avg'] = sum(len_info['arr'])/len(len_info['arr'])

        arr_5 = len_info['arr_5']
        if (len(arr_5) >= 5):
            arr_5.pop(0)
        arr_5.append(len_info['avg'])
            
        len_info['avg_5'] = sum(arr_5)/len(arr_5)
     


##### MEDIA AND STATE DETECTION #####

    def set_state(self):
        # iterate through each flow
        # detect media (active_flows)

        for key in self.flows:
            info = self.flows[key]
            if (info['protocol'] == 'TCP'):
                continue
            
            media_info = self.data[key]['media']
            pps = self.data[key]['pps']
            plen = self.data[key]['len']
            media, state = self.detect_media(plen['max_len'], pps['max_pps'], plen['avg_5'], pps['count'], plen['std'], pps['std'])
            if (state != 'inactive'):
                media_info[media] += 1
                media_info['media'] = self.calculate_media(media_info)              # get which media was set most often for that flow

            media_info['state'] = state
            


    def calculate_media(self, media):
        max_media = ''
        max_count = 0
        if (media['audio'] > max_count):
            max_media = 'audio'
            max_count = media['audio']
        if (media['video'] > max_count):
            max_media = 'video'
            max_count = media['video']
        if (media['content'] > max_count):
            max_media = 'content'
            max_count = media['content']
        if (media['unknown'] > max_count):
            max_media = 'unknown'
            max_count = media['unknown']

        return max_media        


    
    def detect_media(self, max_len, max_bps, curr_len, curr_bps, std_len, std_bps):


        if (max_len < 700 and curr_bps < 70 and curr_bps > 10):
            return 'audio', 'active'


        if (max_len > 800 and curr_bps > 3 and curr_bps < 30 and std_bps< 10):

            return 'video', 'video_minimised'
        
        if (max_len > 800 and std_bps < 50 and curr_bps > 3):

            return 'video', 'video_maximised'

        if (max_len > 800 and std_bps > 10):
            return 'content', 'content_active'

        if (curr_bps < 5 and curr_len > 120):
            return 'content', 'content_still'

        if (curr_bps < 5 and curr_len < 120):
            return  'unknown', 'inactive'


        return 'unknown', 'unknown'


            

##### MESSAGE FORMAT TO SEND/LOG #####

    def construct_msg(self):

            to_send = {}

            self.set_state()                        # media detection
            data_fg = copy.deepcopy(self.data)
            for key in self.flows:

                info = self.flows[key]
                if (info['protocol'] == 'UDP'):
                    loss = data_fg[key]['loss']
                    if (loss['total'] != 0):
                        loss_pc = round(loss['count']/(loss['total'] + loss['count']), 2) * 100
                    else:
                        loss_pc = 0

                   
                    to_send[key] = {
                        'info' : info,
                        'data' : {
                            'pps' : data_fg[key]['pps']['count'],
                            'jitter': data_fg[key]['jitter']['avg'],
                            'loss'  : loss_pc,
                            'media' : data_fg[key]['media']['media'],
                            'state' : data_fg[key]['media']['state'],
                            'len' : data_fg[key]['len']['avg'],
                            'mbps': (data_fg[key]['mbps']['count'] * 8)/1000000,
                        }
                    }

                    self.data[key]['jitter']['all_delay'] = []
                    self.data[key]['jitter']['avg'] = 0
                    self.data[key]['loss']['count'] = 0
                    self.data[key]['loss']['total'] = 0
                    self.data[key]['len']['arr'] = []


                if (info['protocol'] == 'TCP'):
                    to_send[key] = {
                        'info' : info,
                        'data' : {
                            'pps' : data_fg[key]['pps']['count'],
                        }
                    }

                
                
                #logging.debug('Log: %s', log)


                self.data[key]['pps']['count'] = 0
                self.data[key]['mbps']['count'] = 0
                

            return to_send






    
    

