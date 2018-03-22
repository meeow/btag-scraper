import socks
import socket
import requests 
import threading
import logging, sys, re
import smtplib
import time
import random
from stem import Signal
from stem.control import Controller
import tor_requests as tr

_python_version_ = 2.7

#[USER CONFIGUREABLE GLOBAL VARIABLES]==========================================

SITES = [
'https://us.battle.net/forums/en/overwatch/topic/20760857618'
]

KEYWORDS = [
'https://playoverwatch.com/en-us/career/pc/us/'
]

OUT_BTAGS = open('btags.csv', 'w')
OUT_SR = open('sr.csv', 'w')

#[GLOBAL DICTS]=================================================================

_MATCHED_KEYWORDS = dict()
_CURRENT_ROUND = 0
_BTAGS = set()
_SR = dict()
_RANK = dict()

#[BEGIN CODE]===================================================================

def load_file(src, dst):
    srcfile = open(src).readlines()
    for line in srcfile:
        if type(dst) == dict:
            line = line.split(',')
            dst[line[0]] = line[1]
        elif type(dst) == set:
            dst.add(line)
        else: 
            return "dst type not supported. Expect dict or set."

def init_dicts():
    for url in SITES:
        _MATCHED_KEYWORDS[url] = list() 

    for rank in ['bronze','silver','gold','plat','diamond','master','grandmaster']:
        _RANK[rank] = 0

def search_site_for_keyword(url, max_page=2):
    page = 1
    while max_page - page >= 0:
        print 'Searching:', url
        print 'Page:', page

        newurl = url
        if page > 1:
            newurl = url + '?page=' + str(page)

        rawhtml = tr.get_html([newurl], 1, keywords=KEYWORDS)[0]
        if not rawhtml or page >= max_page:
            print KEYWORDS

            # Keyword not found or page limit exceeded
            return

        page += 1
        #Create list of ids
        for line in rawhtml.split('\n'):
            if KEYWORDS[0] in line:
                matchObj = re.search( r'([^/]+)-(\d{4,5})', line)
                btag = matchObj.group(1)+'-'+matchObj.group(2)

                if btag not in _BTAGS:
                    print btag, 'added.', len(_BTAGS)+1, 'tags collected.'
                    _BTAGS.add(btag)

def get_stats(btag):
    url = 'https://playoverwatch.com/en-us/career/pc/' + btag
    rawhtml = tr.get_html([url])[0]
    assert(rawhtml)
    matchObj = re.search(r'u-align-center h5">(\d{3,4})<',rawhtml)
    if not matchObj: 
        return
    sr = int(matchObj.group(1))
    _SR[btag] = sr
    add_to_ranks(sr)

def add_to_ranks(sr):
    if sr >= 4000:
        _RANK['grandmaster'] += 1
    elif sr >= 3500:
        _RANK['master'] += 1
    elif sr >= 3000:
        _RANK['diamond'] += 1
    elif sr >= 2500:
        _RANK['plat'] += 1
    elif sr >= 2000:
        _RANK['gold'] += 1
    elif sr >= 1500:
        _RANK['silver'] += 1
    else:
        _RANK['bronze'] += 1

def dict2csv(d, file):
    dict2list = [(str(k) + ','+ str(d[k]) + '\n') for k in d]
    file.writelines(dict2list)

def set2csv(s, file):
    file.writelines([l + '\n' for l in list(s)])

def main():
    init_dicts()
    #load_file('btags.csv')
    
    for site in SITES:
        search_site_for_keyword(site)
        
    req = 0
    for btag in _BTAGS:
        if req % 5 == 0:
            print "Processed", req, "of", len(_BTAGS) 
        print "Finding SR of", btag, '[' + str(req) + ']'
        get_stats(btag)
        req += 1

    print _SR 
    print _RANK

    set2csv(_BTAGS, OUT_BTAGS)
    dict2csv(_SR, OUT_SR)

main()








