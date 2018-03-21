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

#VERSION: ALPHA 

#[USER CONFIGUREABLE GLOBAL VARIABLES]==========================================

SITES = [
'https://us.battle.net/forums/en/overwatch/topic/20760857618'
]

KEYWORDS = [
'https://playoverwatch.com/en-us/career/pc/us/'
]


IP_CHANGE_ROUNDS = 9

INFO = True

#[NOT OF INTEREST TO USER]======================================================

_MATCHED_KEYWORDS = dict()
_CURRENT_ROUND = 0
_CACHE = set()
_SR = dict()
_RANK = dict()
_TEMPSOCKET = socket.socket
_CONTROLLER = Controller.from_port(port=9051)
print('Controller assigned.')

#[BEGIN CODE]===================================================================

def info(s):
    if INFO:
        print('INFO>', s)

def init_dicts():
    for url in SITES:
        _MATCHED_KEYWORDS[url] = list() 

    for rank in ['bronze','silver','gold','plat','diamond','master','grandmaster']:
        _RANK[rank] = 0

def init_tor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
    socket.socket = socks.socksocket
    info('Tor connected.')
    print_ip()

def print_ip():
    print('IP> ', requests.get("http://icanhazip.com").text[:-1])

def search_site_for_keyword(url, max_page=50):
    page = 1
    while 1:
        if page % 5 == 1: update_ip()
        info('Searching ' + url[:60] + '...')
        info('Page: ' + str(page))
        newurl = url
        if page > 1:
            newurl = url + '?page=' + str(page)
        rawhtml = requests.get(newurl).text
        if "Page Not Found" in requests.get(newurl).text or page >= max_page:
            return

        #Create list of ids
        for line in rawhtml.split('\n'):
            if KEYWORDS[0] in line:
                #print (line)
                matchObj = re.search( r'([^/]+)-(\d{4,5})', line)
                btag = matchObj.group(1)+'-'+matchObj.group(2)

                if btag not in _CACHE:
                    print(btag)
                _CACHE.add(btag)

        page += 1
           
def get_stats(btag):
    url = 'https://playoverwatch.com/en-us/career/pc/' + btag
    rawhtml = requests.get(url).text
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

def update_ip():
    _CONTROLLER.authenticate()
    _CONTROLLER.signal(Signal.NEWNYM)
    print_ip()


def main():
    init_tor()
    init_dicts()
    #updated_site = None
    #sleeptime = random.randrange(10, 30)
    
    for site in SITES:
        try:
            updated_site = search_site_for_keyword(site)
        except requests.exceptions.ConnectionError:
            info('Max requests, updating IP')
            update_ip()
        if updated_site:
            pass
            #email(updated_site)

    #update_ip()
    req = 0
    for btag in _CACHE:
        if req % 7 == 0:
            update_ip()
            print "Processed", req, "of", len(_CACHE) 
        print "Finding SR of", btag, '[' + str(req) + ']'
        get_stats(btag)
        req += 1

    print _SR 
    print _RANK

main()








