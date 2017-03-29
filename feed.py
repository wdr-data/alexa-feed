from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

# @app.route("/1live")
# def einslive():
#    requests.get('')

feeds = {
    'wdr-aktuell': 'https://www1.wdr.de/mediathek/audio/wdr-aktuell/wdr-aktuell-1-100.podcast',
    'wdr-zeitzeichen': 'http://www1.wdr.de/mediathek/audio/zeitzeichen/zeitzeichen-1-100.podcast',
}

@app.route("/<feed>")
def get_feed(feed):
    r = requests.get(feeds[feed])
    return r.text.replace('http://podcast-ww.wdr.de', 'https://media.data.wdr.de')

if __name__ == "__main__":
    app.run()
