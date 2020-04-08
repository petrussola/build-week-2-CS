from api_call import api_call_post, api_call_get_timer
from datetime import datetime

cooldown = 1
now = datetime.now()
shop, now, cooldown = api_call_get_timer("init/", now, cooldown)
# now = datetime.now()
# cooldown = shop["cooldown"]

############################
## CHECK NUMBER TREASURES ##
############################
print(f"==============\n CHECHING STATUS\n============== \n")
status, now, cooldown = api_call_post("status/", now, cooldown, {})
treasures = status["inventory"]
gold = status["gold"]
print(f"++++You have now these treasures:++++\n {treasures}\n")
print(f"****You have this gold:****\n {gold}\n")
# now = datetime.now()
# cooldown = status["cooldown"]

#######################
## SALE OF TREASURES ##
#######################

print(f"==============\n START SALE OF TREASURES\n============== \n")
inventory = status["inventory"]
print(f"You have this much gold in your pocket:\n {inventory}")
for el in status["inventory"]:
    try:
        payload = {
            "name": el
        }
        print(f"Payload to sell, starting: {payload}\n")
        answer, now, cooldown = api_call_post('sell/', now, cooldown, payload)
        print(f"Cooldown: {cooldown}")
        print(f"Now: {now}")
        message = answer["messages"]
        print(f"Answer: {message}")
        print(f">>>The shop keeper tells you:\n {message}\n <<<")
        print(f"Sale finished\n")
        # now = datetime.now()
        # cooldown = answer["cooldown"]
        print(f"==============\n SALE COMPLETED> STARTING CONFIRMATION\n============== \n")
        if len(answer["messages"]) > 0:
            payload = {
                "name": el,
                "confirm": "yes"
            }
            try:
                print(f"Payload to confirm sale, starting: {payload}\n")
                answer, now, cooldown = api_call_post("sell/", now, cooldown, payload)
                print(f"Confirm sale finished\n")
            except:
                print(">>>> There was a problem confirming the sale. <<<<\n\n")
    except:
        print(">>>> There was a problem selling the treasure. <<<<\n\n")
    status, now, cooldown = api_call_post("status/", now, cooldown, {})
    treasures = status["inventory"]
    gold = status["gold"]
    print(f"++++You have now these treasures:++++\n {treasures}\n")
    print(f"****You have this gold:****\n {gold}\n")
    # now = datetime.now()
    # cooldown = shop["cooldown"]
    print(f"==============\n SALE CONFIRMED\n============== \n")