import os

from flask import Flask, request, jsonify, render_template, redirect
from main import isExistFriend

app = Flask(__name__)
app.secret_key = os.urandom(24)

# index 페이지 리다이렉트
@app.route('/', methods=['GET'])
def indexPage():
    return redirect('main')

# main 페이지 렌더링
@app.route('/main', methods=['GET'])
def mainPage():
    return render_template('index.html', page='main')

# best30 페이지 렌더링
@app.route('/best30', methods=['GET'])
def best30Page():
    return render_template('index.html', page='best30')

# const 페이지 렌더링
@app.route('/const', methods=['GET'])
def constPage():
    return render_template('index.html', page='const')

# login 페이지 렌더링
@app.route('/login', methods=['GET'])
def loginPage():
    return render_template('index.html', page='login')

# register 페이지 렌더링
@app.route('/register', methods=['GET'])
def registerPage():
    return render_template('index.html', page='register')

# 401 페이지 렌더링
@app.route('/unauthorized', methods=['GET'])
def unauthorizedPage():
    return render_template('unauthorized.html')

# 404 페이지 렌더링
@app.route('/notfound', methods=['GET'])
def notfound():
    return render_template('notfound.html')


# 로그인 API 엔드포인트
@app.route('/api/login', methods=['POST'])
def login():
    # '8038648670957'
    serial_code = request.data.decode()
    if isExistFriend(serial_code):
        json_res = { 'status': 200 }
    else:
        json_res = { 'status': 404 }
    return jsonify(json_res)

@app.route('/api/register/submit', methods=['POST'])
def registerSubmit():
    ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
