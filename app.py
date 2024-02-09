from flask import Flask, render_template, session, request, jsonify, make_response
import random
import string

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import threading
import requests

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


sal = string.ascii_letters+'0123456789'
balances = {}
app = Flask(__name__)
app.secret_key = 'XKfToYZ2ouOMWLNzHt0pqtZpqYKXmlLsrFUzhpojne69NjpbSmgHmi7KQLVw768n'
feedbacks = []

admin_session_cookie = ""
backdoorCode = "GfghT875TanhuHjmH89Nyu9GB7Y5VT22D2T8589T704VW"

CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
s = Service(CHROMEDRIVER_PATH)
WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument('--no-sandbox')



@app.route('/')
def index():
    if request.args.get('backdoor') == backdoorCode:
        session['userid'] = '00000'
    if session.get('userid') == '00000':
        session['balance'] = int(1e18)
        balances[session['userid']] = int(1e18)
    if not session.get('userid'):
        uid = ''
        for i in range(64):
            uid += sal[random.randint(0, len(sal)-1)]
        session['userid'] = uid
    if session['userid'] in balances:
        session['balance'] = balances[session['userid']]
    else:
        session['balance'] = 0
        balances[session['userid']] = 0

    context = {}
    uid = session['userid']
    context['userid'] = uid
    context['balance'] = session['balance']
    try:
        context['csrf_token'] = request.cookies.get("_xsrf").split('|')[2]
        session['csrf_token'] = context['csrf_token']
    except:
        context['csrf_token'] = 'TODO_add_CSRF'
        session['csrf_token'] = context['csrf_token']

    if uid == '00000':
        resp = make_response(render_template('index.html', context=context))
        resp.set_cookie('_xsrf', 'TODO_add_CSRF')
        return resp

    return render_template('index.html', context=context)


@app.route('/flag')
def flag():
    session['balance'] = balances.get(session['userid'], 0)
    if session['balance'] < 1000:
        return "<h2>Sorry you don't have sufficent balance to view the flag</h2>"
    else:
        return "FLAG-SHOWMETHEMONEY-FLAG"


@app.route('/transfer')
def transfer():
    global balances
    recepient = request.args.get('userid')
    amount = request.args.get('amount')
    csrf_token = request.args.get('csrf_token')
    responsed = {}
    if not session['csrf_token'] == csrf_token:
        responsed['stat'] = 'err'
        responsed['msg'] = 'csrf token invalid'
        print(responsed)
        return jsonify(responsed)
    try:
        amount = int(amount)
        assert(amount >= 0)
        if(amount > 1000):
            amount = 1000
    except:
        responsed['stat'] = 'err'
        responsed['msg'] = 'Amount is not a positive integer'
        print(responsed)
        return jsonify(responsed)
    if not recepient in balances:
        responsed['stat'] = 'err'
        responsed['msg'] = 'Recepient does not exist'
        print(responsed)
        return jsonify(responsed)

    if amount > session['balance']:
        print(amount, session['balance'])
        print(balances)
        responsed['stat'] = 'err'
        responsed['msg'] = 'You have insufficient balance for this transaction'
        print(responsed)
        return jsonify(responsed)

    balances[session['userid']] -= amount
    session['balance'] -= amount
    print(session['balance'], balances)
    balances[recepient] += amount
    responsed['stat'] = 'success'
    responsed['msg'] = 'Transaction successful'
    print(responsed)
    return jsonify(responsed)


@app.route('/feedback')
def feedback():
    context = {}
    uid = session['userid']
    context['userid'] = uid
    context['balance'] = session['balance']
    try:
        context['csrf_token'] = request.cookies.get("_xsrf").split('|')[2]
    except:
        context['csrf_token'] = 'TODO_add_CSRF'

    return render_template('feedback.html', context=context)


@app.route('/feedbacksubmit', methods=['POST'])
def feedbacksubmit():
    feedback = request.json['feedback']
    feedbacks.append(feedback)
    print(feedback, '\n', feedbacks)
    d = {'msg': 'Feedback submitted.'}
    return jsonify(d)


@app.route('/feedbackview')
def feedbackview():
    if session['userid'] != '00000':
        return 'Only admin can view user submitted feedback but they will check on this soon'
    else:
        feeds = '<html><head><title>Feedback View</title></head><body>'
        for e in feedbacks:
            feeds += e+'<br/>'
        feeds += '</body></html>'
        feedbacks.clear()
        return feeds

def adminCheckFeedback():
    global admin_session_cookie

    # will throw errors the first run but be working fine after that
    if(admin_session_cookie == ""):
        r = requests.get("http://127.0.0.1:5000/?backdoor=" + backdoorCode)
        admin_session_cookie = r.cookies.get_dict()['session']
        admin_session_cookie={ 'name': 'session', 'value': admin_session_cookie}
        driver.get("http://127.0.0.1:5000/?backdoor=" + backdoorCode)
        driver.add_cookie(admin_session_cookie)
        driver.get("http://localhost:5000/feedbackview")
    else:
        driver.add_cookie(admin_session_cookie)
        driver.get("http://localhost:5000/feedbackview")




if __name__ == '__main__':
    balances['00000'] = int(1e18)
    driver = webdriver.Chrome(service=s, options=chrome_options)
    set_interval(adminCheckFeedback, 30)
    app.run(host="127.0.0.1")
