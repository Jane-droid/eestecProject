import nltk.data
#from textFromWebsite import google_search

def split_in_sentences(data):
    my_list = nltk.tokenize.sent_tokenize(data)
    final_list = []
    buffer = ""
    count = 0
    for sentence in my_list:
        if count < 7:
            buffer = buffer + " " + sentence
            count = count + 1
        else:
            final_list.append(buffer)
            buffer = ""
            count = 0
            
    return final_list

#print(split_in_sentences(google_search("Which ocean is Bermuda in?")))