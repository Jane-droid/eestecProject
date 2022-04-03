def recognise_year(str):
    words = str.split()
    for word in words:
        if word.isnumeric() and len(word) > 2:
            return word
    return str