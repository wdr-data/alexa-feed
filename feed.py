import json
from datetime import datetime
import locale
from glob import glob
import os

from flask import Flask, Response
import requests
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_TIME, "C")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, static_folder='wdraktuell', static_url_path='/static')


# @app.route("/1live")
# def einslive():
#    requests.get('')

SINGLE_AUDIO = {
  "uid": None,
  "updateDate": None,
  "titleText": None,
  "mainText": "",
  "streamUrl": None,
  "redirectionUrl": None
}

PODCAST_URL = 'https://www1.wdr.de/mediathek/audio/%s.podcast'
HTML_URL = 'https://www1.wdr.de/mediathek/audio/%s.html'

@app.route("/wdraktuell-hourly")
def wdraktuell_hourly():
    f = max([os.path.basename(path) for path in glob('wdraktuell/WDRAKTUELL*')])
    
    resp = SINGLE_AUDIO.copy()
    resp['uid'] = os.path.splitext(f)[0]
    update_time = datetime.strptime(f, 'WDRAKTUELL-%Y%m%d%H%M.mp3')
    resp['updateDate'] = update_time.strftime('%Y-%m-%dT%H:%M:%S.0Z')  # 2017-04-10T16:00:16.0Z
    resp['titleText'] = "WDR Aktuell"
    resp['streamUrl'] = 'https://feeds.data.wdr.de/static/' + f
    resp['redirectionUrl'] = "www1.wdr.de/mediathek/audio/wdr-aktuell/wdr-aktuell-140.podcast"
    
    return Response(json.dumps(resp), mimetype='application/json')


@app.route("/<path1>.podcast")
@app.route("/<path1>/<path2>.podcast")
@app.route("/<path1>/<path2>/<path3>.podcast")
def get_feed(path1=None, path2=None, path3=None):
    feed = '/'.join(filter(bool, (path1, path2, path3)))

    r = requests.get(PODCAST_URL % feed)
    
    if r.status_code == 404:
        return 'Resource %s not found' % PODCAST_URL % feed, 404

    soup = BeautifulSoup(r.text, 'lxml')
    resp = SINGLE_AUDIO.copy()
    chan = soup.rss.channel

    resp['uid'] = chan.guid.string
    # Mon, 10 Apr 2017 16:00:16 GMT
    update_time = datetime.strptime(chan.lastbuilddate.string, '%a, %d %b %Y %H:%M:%S %Z')
    resp['updateDate'] = update_time.strftime('%Y-%m-%dT%H:%M:%S.0Z')  # 2017-04-10T16:00:16.0Z
    resp['titleText'] = chan.title.string
    resp['streamUrl'] = chan.item.enclosure['url'].replace('http://podcast-ww.wdr.de', 
                                                           'https://media.data.wdr.de')
    resp['redirectionUrl'] = HTML_URL % feed
    
    return Response(json.dumps(resp), mimetype='application/json')

if __name__ == "__main__":
    app.run()
