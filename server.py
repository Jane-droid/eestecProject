import random
import string
from urllib import response
import flask
from flask import jsonify, request
from temp import get_answer
from test_client_example import CompetitionBot

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/sanity', methods=['GET'])
def check_sanity():
    response = jsonify({
        "status": "ok"
    })
    response.status_code = 200
    return response

@app.route('/question', methods=['POST'])
def question():
    question_contents = request.get_json() 
    query = question_contents["question_text"]
    answer= jsonify({
        "answer": get_answer(query).capitalize()
    })
    answer.status_code=200
    return answer

app.run(port=5000)