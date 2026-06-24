def label(status):
    if status == "open":
        return "Open"
    elif status == "closed":
        return "Closed"
    elif status == "pending":
        return "Pending"
    else:
        return "Unknown"


def shout(text):
    return text.upper() + "!"
