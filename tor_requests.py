import socks
import socket
import requests 
import threading
import copy
from stem import Signal
from stem.control import Controller

_PYTHON_VERSION_ = 2.7

# Number of requests to make (excluding printing IP) before refreshing IP 
IP_CHANGE_ROUNDS = 9
_ELAPSED_ROUNDS = 0

# Used for tor
_TEMPSOCKET = socket.socket
try:
    _CONTROLLER = Controller.from_port(port=9051)
except:
    print "Fatal controller error. Is tor running?"
    exit()
_tor_connected = False

#===============================================================================

def print_ip():
    print 'IP> ', tor_get("http://icanhazip.com").text[:-1]

def _update_ip():
    _CONTROLLER.authenticate()
    _CONTROLLER.signal(Signal.NEWNYM)
    print_ip()

def _init_tor():
    global _tor_connected
    if _tor_connected: return

    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
        socket.socket = socks.socksocket
    except socks.SOCKS5Error:
        print 'Fatal socks error.'
        return
        
    _tor_connected = True
    print_ip()

def tor_get(url):
    global _ELAPSED_ROUNDS

    if not _tor_connected:
        _init_tor()
    _ELAPSED_ROUNDS += 1
    if _ELAPSED_ROUNDS % IP_CHANGE_ROUNDS == 0:
        _update_ip() 

    request = ''
    while not request:
        try:
            request = requests.get(url)
        except requests.exceptions.ConnectionError:
            print 'Request error, updating IP and trying again.'
            update_ip()

    return request

# @param urls: list of urls to scrape
# @param searchnum:
#   'all': all keywords must be present in the html file corresponding to url
#   \d: at least searchnum number of keywords must be present 
# @param keywords: list of keywords to search for
# @return: list where each element is one html page
def get_html(urls, searchnum='all' , keywords=None):
    if searchnum != 'all' and type(searchnum) is not int:
        return "Error: searchnum not properly defined"
    if not urls: return "Error: URLs missing."

    saved_pages = []
    for url in urls:
        rawhtml = tor_get(url).text
        if keywords:
            kwlist, kwlistlen = copy.deepcopy(keywords), len(keywords)
            for line in rawhtml.split('\n'):
                for kw in kwlist:
                    if kw in line:
                        kwlist.remove(kw)
            if kwlist and searchmode == 'all':
                print "Not all keywords found."
                saved_pages.append(None)
            elif len(kwlist) == kwlistlen:
                print "No keywords found."
                saved_pages.append(None)
            elif not kwlistlen - len(kwlist) <= searchnum:
                print "Not enough keywords found."
                saved_pages.append(None)
        saved_pages.append(rawhtml)
             
    return saved_pages



