
def string_formatter(string):
    string = string.lower().strip()
    string = ''.join(ch for ch in string if ch.isspace() or ch.isalpha())
    return string
