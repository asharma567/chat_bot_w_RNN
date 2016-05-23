#!flask/bin/python
from flask import Flask, jsonify
import analysis

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/here', methods=['GET'])
def newIndex():
    return "Hello, World!"

@app.route('/search/<path:search_term>', methods=['GET'])
def get_tasks(search_term):
    myTerm = search_term.replace('+',' ')
    results = analysis.findPhrase(myTerm)
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')