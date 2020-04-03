from api_call import api_call_post
from datetime import datetime

payload = {}

now = datetime.now()

cooldown = 2

status = api_call_post("status/", now, cooldown, payload)
print(status)