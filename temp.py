import torch
from textFromWebsite import google_search
from split import split_in_sentences
from transformers import BertForQuestionAnswering
from transformers import BertTokenizerFast
from year import recognise_year

model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer = BertTokenizerFast.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')


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
    
    return answer
    

def get_answer(question):
    
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
        if question.split()[0] == "When":
            final_answer = recognise_year(final_answer)
        return final_answer.capitalize()
    else:
        maxim = 0
        key = ""
        for (answer, freq) in answers.items():
            if freq > maxim:
                maxim = freq
                key = answer
        if question.split()[0] == "When":
            key = recognise_year(key)
        return key.capitalize()
    
def get_answer_multiple_choice(question, choices):
    
    text = google_search(question)
    answers = {}
    for choice in choices:
        answers[choice] = 0
    lines = split_in_sentences(text, question)
    for par in lines:
        curr_answer = question_answer(question, par)
        if len(curr_answer.split()) < 10:
            for word in curr_answer.split():
                for choice in choices:
                    if word.lower() in choice.lower():
                        answers[choice] += 1
    max = 0
    answer = 'idk'
    for choice in choices:
        if answers[choice] > max:
            max = answers[choice]
            answer = choice
    if answer != "idk" and question.split()[0] == "When":
        answer = recognise_year(answer)
    return answer
            

