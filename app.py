from flask import Flask,make_response,request,jsonify
import hashlib
import requests
import os

app = Flask(__name__)

@app.route("/api/v1/task",methods=['GET'])
def task():
    try:
        query_string = request.query_string.decode('utf-8')
        split_data = query_string.split('&')
        inp_data = {}
        for item in split_data:
            key,val = item.split('=')
            inp_data[key] = val
        print(inp_data)
        # return make_response(jsonify({'message':'success'}))
        sess = requests.session()
        get_key_url = 'http://36.255.68.39:8082/key.jsp?actionId=getKey'
        resp = sess.get(get_key_url)
        data = resp.json()
        key = data.get('key')
        ip = data.get('ip')
        jsessionid = data.get('JSessionId')
        ##### LEVEL 1 ENCRYPTION ******************
        user = inp_data.get('owner')
        password = os.environ.get('MAINBERG_PASSWORD')
        plain_text = (user+':'+ip+':'+password).encode('utf-8')
        print(plain_text)
        level_1_encrypt = hashlib.sha256(plain_text).hexdigest()
        ##### LEVEL 2 ENCRYPTION ******************
        level_2_plain_text = (level_1_encrypt + ':' + key).encode('utf-8')
        level_2_encrypt = hashlib.sha256(level_2_plain_text).hexdigest()

        login_url = 'http://36.255.68.39:8082/InternalUserServlet?actionId=userLoginWithJson&userId='+user+'&password='+level_2_encrypt
        login_resp = sess.get(login_url)
        print(login_resp.json())
        campaign_url =  'http://36.255.68.39:8082/campaign/api.jsp'
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        campaign_resp = sess.post(url=campaign_url,data=inp_data,headers=headers)
        return make_response(campaign_resp.json()),campaign_resp.status_code
    except Exception as e:
        print(e)
        return make_response(jsonify({"message":"fail"})),400


@app.route("/api/v1/alive")
def alive():
    return {"msg": "alive"}

if __name__ == "__main__":
    print("Inside main")
    app.run(host="localhost",port=8080,debug=True)