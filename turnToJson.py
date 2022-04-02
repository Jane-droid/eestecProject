import json

def createJsonObject(answer):
    answer_before_json = {"answer": answer}
    
    answer_json = json.dumps(answer_before_json)
    print(answer_json)
    return answer_json
