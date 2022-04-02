import pandas as pd
import numpy as np
import torch
from transformers import BertForQuestionAnswering
from transformers import BertTokenizer
from textFromWebsite import google_search
from split import split_in_sentences




coqa = pd.read_json('http://downloads.cs.stanford.edu/nlp/data/coqa/coqa-train-v1.0.json')
coqa.head()
del coqa["version"]

#required columns in our dataframe
cols = ["text","question","answer"]
#list of lists to create our dataframe
comp_list = []
for index, row in coqa.iterrows():
    for i in range(len(row["data"]["questions"])):
        temp_list = []
        temp_list.append(row["data"]["story"])
        temp_list.append(row["data"]["questions"][i]["input_text"])
        temp_list.append(row["data"]["answers"][i]["input_text"])
        comp_list.append(temp_list)
new_df = pd.DataFrame(comp_list, columns=cols) 
#saving the dataframe to csv file for further loading
new_df.to_csv("CoQA_data.csv", index=False)

model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

data = pd.read_csv("CoQA_data.csv")
data.head()

random_num = np.random.randint(0,len(data))
question = data["question"][random_num]
text = data["text"][random_num]

#print("Number of question and answers: ", len(data))


input_ids = tokenizer.encode(question, text)
#print("The input has a total of {} tokens.".format(len(input_ids)))


tokens = tokenizer.convert_ids_to_tokens(input_ids)
    
    
#first occurence of [SEP] token
sep_idx = input_ids.index(tokenizer.sep_token_id)
#print("SEP token index: ", sep_idx)
#number of tokens in segment A (question) - this will be one more than the sep_idx as the index in Python starts from 0
num_seg_a = sep_idx+1
#print("Number of tokens in segment A: ", num_seg_a)
#number of tokens in segment B (text)
num_seg_b = len(input_ids) - num_seg_a
#print("Number of tokens in segment B: ", num_seg_b)
#creating the segment ids
segment_ids = [0]*num_seg_a + [1]*num_seg_b
#making sure that every input token has a segment id
assert len(segment_ids) == len(input_ids)



#token input_ids to represent the input and token segment_ids to differentiate our segments - question and text
output = model(torch.tensor([input_ids]),  token_type_ids=torch.tensor([segment_ids]))



#tokens with highest start and end scores
answer_start = torch.argmax(output.start_logits)
answer_end = torch.argmax(output.end_logits)
if answer_end >= answer_start:
    answer = " ".join(tokens[answer_start:answer_end+1])
#else:
    #print("I am unable to find the answer to this question. Can you please ask another question?")
    
#print("\nQuestion:\n{}".format(question.capitalize()))
#print("\nAnswer:\n{}.".format(answer.capitalize()))



answer = tokens[answer_start]
for i in range(answer_start+1, answer_end+1):
    if tokens[i][0:2] == "##":
        answer += tokens[i][2:]
    else:
        answer += " " + tokens[i]
        

def most_frequent(List):
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
    
    lines = split_in_sentences(text);
    answers = []
    for par in lines:
        answers.append(question_answer(question, par))
    
    answers = list(filter(lambda x: x != "Unable to find the answer to your question.", answers))
    answers = list(filter(lambda x: len(x.split()) < 10, answers))
    answers = list(filter(lambda x: (question.replace('?','').lower() in x) == False, answers))
    print(answers)
    answer = most_frequent(answers).capitalize()
    print("Predicted answer:\n" + answer)
    
    flag = True
    flag_N = False
    
    more = input("Do you want to choose another text?[Y/N]\n")
    if more[0] == 'N':
        flag_N = True
            
    if flag_N == True:
        break

