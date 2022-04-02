def is_multiple_choice_answer(answer, choices):
    for word in answer.split(): 
        for choice in choices:
            if word in choice.lower():
                return choice
        
    return ''

#print(is_multiple_choice_answer("ritchie", ["Bjarne Stroustrup","Dennis Ritchie","Bill Gates","James Gosling"]))