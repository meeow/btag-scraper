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

#[NOT OF INTEREST TO USER]======================================================

_MATCHED_KEYWORDS = dict()
_CURRENT_ROUND = 0
_CACHE = set()
_SR = dict()
_RANK = dict()


#[BEGIN CODE]===================================================================

def init_dicts():
    for url in SITES:
        _MATCHED_KEYWORDS[url] = list() 

    for rank in ['bronze','silver','gold','plat','diamond','master','grandmaster']:
        _RANK[rank] = 0

def search_site_for_keyword(url, max_page=50):
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

                if btag not in _CACHE:
                    print btag, 'added.', len(_CACHE)+1, 'tags collected.'
                    _CACHE.add(btag)

def get_stats(btag):
    url = 'https://playoverwatch.com/en-us/career/pc/' + btag
    rawhtml = tr.get_html([url])
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

def main():
    init_dicts()
    
    for site in SITES:
        search_site_for_keyword(site)
        
    req = 0
    for btag in _CACHE:
        if req % 5 == 0:
            print "Processed", req, "of", len(_CACHE) 
        print "Finding SR of", btag, '[' + str(req) + ']'
        get_stats(btag)
        req += 1

    print _SR 
    print _RANK

main()








