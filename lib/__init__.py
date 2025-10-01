from datetime import datetime

def now():
    date=datetime.now().isoformat()
    return date.split(".")[0]
    