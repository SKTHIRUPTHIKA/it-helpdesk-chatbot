def classify_issue(text):
    text = text.lower()

    if any(word in text for word in ["wifi", "network", "internet", "lan"]):
        return "Network"
    elif any(word in text for word in ["software", "app", "install", "update"]):
        return "Software"
    elif any(word in text for word in ["keyboard", "mouse", "screen", "hardware"]):
        return "Hardware"
    else:
        return "Other"