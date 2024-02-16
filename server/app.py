import os

from flask import Flask, jsonify, render_template, redirect

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 인덱스 페이지 렌더링 ( 리다이렉트 )
@app.route('/', methods=['GET'])
def indexPage():
    return redirect('main')

# 메인 페이지 렌더링
@app.route('/main', methods=['GET'])
def mainPage():
    return render_template('index.html', content='main')

# 401 페이지 렌더링
@app.route('/unauthorized', methods=['GET'])
def unauthorizedPage():
    return render_template('unauthorized.html')

# 로그인 API 엔드포인트
@app.route('/api/login', methods=['POST'])
def login():
    json_res = { 'key': 'value' }
    return jsonify(json_res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
