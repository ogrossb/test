
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, make_response
from Trade_Deadline_Landscape_v3 import GetTradeDeadlineLandscape
from TrackmanWeb import GetTrackmanLogs
import time

app = Flask(__name__)
app.config["DEBUG"] = False

@app.route('/')
def hello_world():
    return '''
        <html>
            <body>
                <div>
                    <h1>Welcome to ABoothInTheWild's Python Web App!</h1>
                </div>
                <div>
                    <p>Click <a href=http://aboothinthewild.pythonanywhere.com/getLandscape>this link</a> to download today's Trade Deadline Landscape</p>
                    <p>Landscape includes FiveThirtyEight's MLB Playoff Odds, and Fangraphs' organizational position rankings, by fWAR.</p>
                </div>
            </body>
        </html>
    '''

@app.route('/getLandscape')
def test():
    data = GetTradeDeadlineLandscape()
    resp = make_response(data.to_csv(index=False))
    resp.headers["Content-Disposition"] = "attachment; filename=tradeDeadlineLandscape_" + time.strftime('%Y%m%d') + ".csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp

@app.route('/getTrackmanLogs')
def getTrackmanLogs():
    memory_file = GetTrackmanLogs()
    resp = make_response(memory_file)
    resp['Content-Type'] = 'application/x-zip-compressed'
    resp['Content-Disposition'] = 'attachment; filename=trackman_daily_status_' + time.strftime('%Y%m%d') + '.zip'
    return resp