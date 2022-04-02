import json

# JSON-UL CARE URMEAZA SA FIE PARSAT TREBUIE SA FIE STRING!!!
questionJson = '{"question_text": "Who became the first king of a united Italy in 1861?","question_type": "direct_answer","question_category": "History","answer_choices": [],"answer_type": "text"}'


class questionFormat:
    text: str
    question_type: str
    category: str
    answer_choices: list
    answer_type: str

question = questionFormat()

q_helper = json.loads(questionJson)

question.text = q_helper["question_text"]
question.question_type = q_helper["question_type"]
question.category = q_helper["question_category"]
question.answer_choices = q_helper["answer_choices"]
question.answer_type = q_helper["answer_type"]

#QUESTION E STRUCTURAAAAA
