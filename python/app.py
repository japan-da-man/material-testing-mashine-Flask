#https://hirahira.blog/pyhton-flask-login/
from flask import Flask, request, render_template, redirect, url_for, flash, make_response, session, Response
from camera import VideoCamera
from arduino import Arduino

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['USERNAME'] = 'Group_A'
app.config['PASSWORD'] = 'pass'

camera = VideoCamera()

job = None

@app.route('/')
def index():
    if "flag" in session and session["flag"]:
        return render_template('welcome.html', username=session["username"])
    return redirect('/login')
    

@app.route('/login', methods=['GET'])
def login():
    if "flag" in session and session["flag"]:
        return redirect('/welcome')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    if username != app.config['USERNAME']:
        flash('ユーザ名が異なります')
        return redirect('/login')
    elif password != app.config['PASSWORD']:
        flash('パスワードが異なります')
        return redirect('/login')
    else:
        session["flag"] = True
        session["username"] = username
    if session["flag"]:
        return render_template('welcome.html', username=session["username"])
    else:
        return redirect('/login')


@app.route('/welcome')
def welcome():
    if "flag" in session and session["flag"]:
        return render_template('welcome.html', username=session["username"])
    return redirect('/login')

@app.route('/contents', methods=['GET','POST'])
def contents():
    global job
    if "flag" in session and session["flag"]:
        if job is None:
            if request.method == 'GET':
                return render_template('contents.html', username=session["username"])
            else:
                job = Arduino()
                job.start()
        return render_template('measure.html', username=session["username"])
    return redirect('/login')


@app.route('/measure', methods=['GET', 'POST'])
def measure():
    global job
    if "flag" in session and session["flag"]:
        if job is not None:
            if request.method == 'GET':
                return render_template('measure.html', username=session["username"])
            else:
                if 'stop_cy' in request.form:
                    job.stop_cy()
                    job.join()
                    job = None
                    return render_template('contents.html', username=session["username"])
                elif 'cycle' in request.form:
                    job.cycle()
                elif 'reset' in request.form:
                    job.reset()
            return render_template('measure.html', username=session["username"])
        return render_template('measure.html', username=session["username"])
    return redirect('/login')

def video_gen():
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +frame+ b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(video_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


def plot_gen():
    global job
    while job is not None:
        frame = job.get_frame()
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/plot_feed')
def plot_feed():
    return Response(plot_gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/plot_data')
def plot_data():
    response = make_response(Arduino.plot_data())
    response.headers['Content-Type'] = 'image/svg+xml'
    return response


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop("flag", None)
    session["username"] = None
    session["flag"] = False
    flash('ログアウトしました')
    return redirect("/login")



if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0') # こちらを有効にすると外部からアクセスできるようになる
