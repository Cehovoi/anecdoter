
def string_formatter(string):
    string = string.lower().strip()
    string = ''.join(ch for ch in string if ch.isspace() or ch.isalpha())
    if not string or len(string) < 3 or len(string) > 100 or string.isspace():
        return None
    return string


def dic_shortener(original_dict, needless_keys):
    return {key: value for key, value in
            original_dict if key not in needless_keys}
