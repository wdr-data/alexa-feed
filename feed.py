import json
from datetime import datetime
import locale

from flask import Flask, Response
import requests
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_TIME, "C")

app = Flask(__name__)


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

PODCAST_URL = 'https://www1.wdr.de/mediathek/audio/%s/%s.podcast'
HTML_URL = 'https://www1.wdr.de/mediathek/audio/%s/%s.html'

feeds = {
    'wdr-aktuell': ('wdr-aktuell', 'wdr-aktuell-1-100'),
    'wdr-zeitzeichen': ('zeitzeichen', 'zeitzeichen-1-100'),
    '1live-infos': ('1live/infos', 'infos-1-100'),
    'wdr2-stichtag': ('wdr2/wdr2-stichtag', 'stichtag-1-100'),
}

@app.route("/<feed>")
def get_feed(feed):
    if feed not in feeds:
        return '', 404

    r = requests.get(PODCAST_URL % feeds[feed])
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
    resp['redirectionUrl'] = HTML_URL % feeds[feed]
    
    return Response(json.dumps(resp), mimetype='application/json')

if __name__ == "__main__":
    app.run()
