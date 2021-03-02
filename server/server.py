from flask import Flask, render_template
import requests
app = Flask(__name__)

@app.route('/')
def hello_world():

    try:
        r = requests.get('http://infrastructure:8080')
        data = r.json()
        return render_template('main.html', state=data['status'], updated=data['time_of_decision'])
    except:
        return render_template('main.html', state='None', updated='None')
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)