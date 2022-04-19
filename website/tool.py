import re

def stripStr(text):
    if text is not None:
        return text.strip()
    else:
        return text 

def utf8len(s,max_len):
    len(s.encode('utf-8')) > max_len
    return 

def checkLength(text,max):
    chinese_len = len(re.findall(r"[\u4e00-\u9fa5]",text))
    other_len = len(text)-chinese_len
    total_len = chinese_len*4 + other_len
    print("total_len",total_len)
    return total_len > max