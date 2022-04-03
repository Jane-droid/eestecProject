import torch
from textFromWebsite import google_search
from split import split_in_sentences
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer

model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


def most_frequent(List):
    if len(List) == 0:
        return ''
    counter = 0
    el = List[0]
     
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            el = i
 
    return el


def question_answer(question, text):
    
    #tokenize question and text as a pair
    input_ids = tokenizer.encode(question, text)

    if(len(input_ids) > 512):
        return "Unable to find the answer to your question."

    #string version of tokenized ids
    tokens = tokenizer.convert_ids_to_tokens(input_ids)
    
    #segment IDs
    #first occurence of [SEP] token
    sep_idx = input_ids.index(tokenizer.sep_token_id)
    #number of tokens in segment A (question)
    num_seg_a = sep_idx+1
    #number of tokens in segment B (text)
    num_seg_b = len(input_ids) - num_seg_a
    
    #list of 0s and 1s for segment embeddings
    segment_ids = [0]*num_seg_a + [1]*num_seg_b
    assert len(segment_ids) == len(input_ids)
    
    #model output using input_ids and segment_ids
    output = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))
    
    #reconstructing the answer
    answer_start = torch.argmax(output.start_logits)
    answer_end = torch.argmax(output.end_logits)
    answer = "[CLS]"
    if answer_end >= answer_start:
        answer = tokens[answer_start]
        for i in range(answer_start+1, answer_end+1):
            if tokens[i][0:2] == "##":
                answer += tokens[i][2:]
            else:
                answer += " " + tokens[i]
                
    if answer.startswith("[CLS]"):
        answer = "Unable to find the answer to your question."
    
    #print("\nPredicted answer:\n{}".format(answer.capitalize()))
    return answer
    

while True:
    
    question = input("Please enter your question: \n")
    text = google_search(question)
    
    lines = split_in_sentences(text, question)
    answers = {}
    final_answer = "idk"
    for par in lines:
        curr_answer = question_answer(question, par)
        if curr_answer in answers:
            answers[curr_answer] += 1
            if answers[curr_answer] > 4:
                final_answer = curr_answer
                break
        else:
            if curr_answer != "Unable to find the answer to your question.":
                if curr_answer != "[SEP]":
                    if len(curr_answer.split()) < 10:
                        if (question.replace('?','').lower() in curr_answer) == False:
                            answers[curr_answer] = 1
    if final_answer != "idk":
        print("Predicted answer:\n" + final_answer.capitalize())
    else:
        maxim = 0
        key = ""
        for (answer, freq) in answers.items():
            if freq > maxim:
                maxim = freq
                key = answer
        print("Predicted answer:\n" + key.capitalize())

    flag = True
    flag_N = False
    
    more = input("Do you want to choose another text?[Y/N]\n")
    if more[0] == 'N':
        flag_N = True
            
    if flag_N == True:
        break

