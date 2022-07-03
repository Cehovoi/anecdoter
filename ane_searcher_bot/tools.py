
def string_formatter(string):
    string = string.lower().strip()
    string = ''.join(ch for ch in string if ch.isspace() or ch.isalpha())
    return string


def dic_shortener(original_dict, needless_keys):
    return {key: value for key, value in
            original_dict if key not in needless_keys}
