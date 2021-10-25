from flask import Flask,make_response,request,jsonify
import hashlib
import requests
import os

app = Flask(__name__)

@app.route("/api/v1/task",methods=['POST'])
def task():
    try:
        sess = requests.session()
        get_key_url = 'http://36.255.68.39:8082/key.jsp?actionId=getKey'
        resp = sess.get(get_key_url)
        data = resp.json()
        key = data.get('key')
        ip = data.get('ip')
        jsessionid = data.get('JSessionId')
        ##### LEVEL 1 ENCRYPTION ******************
        user = 'testclient'
        password = os.environ.get('MAINBERG_PASSWORD')
        plain_text = (user+':'+ip+':'+password).encode('utf-8')
        level_1_encrypt = hashlib.sha256(plain_text).hexdigest()
        ##### LEVEL 2 ENCRYPTION ******************
        level_2_plain_text = (level_1_encrypt + ':' + key).encode('utf-8')
        level_2_encrypt = hashlib.sha256(level_2_plain_text).hexdigest()

        login_url = 'http://36.255.68.39:8082/InternalUserServlet?actionId=userLoginWithJson&userId='+user+'&password='+level_2_encrypt
        login_resp = sess.get(login_url)
        print(login_resp.json())
        campaign_url =  'http://36.255.68.39:8082/campaign/api.jsp'
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = {}
        for tmp_key,val in request.form.items():
            data[tmp_key] = val
        campaign_resp = sess.post(url=campaign_url,data=data,headers=headers)
        return make_response(campaign_resp.json()),campaign_resp.status_code
    except Exception as e:
        print(e)
        return make_response(jsonify({"message":"fail"})),400


@app.route("/api/v1/alive")
def alive():
    return {"msg": "alive"}

if __name__ == "_main_":
    app.run(host="0.0.0.0",port=8080)