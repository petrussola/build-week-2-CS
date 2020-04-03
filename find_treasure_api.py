import time
from datetime import datetime
from api_call import api_call_post, api_call_get


def findSomethingApi(listRooms, listDirections, now, cooldown):
    print(f"&&& The list of rooms is: &&&\n {listRooms}\n")
    print(f"&&& The list of directions is: &&&\n {listDirections}\n")
    current_room = None
    if len(listDirections) > 0:
        for i in range(len(listRooms) - 1):
            try:
                # we pass the direction and the next room as payload so we can avail of wise explorer cooldown reduction
                payload = {"direction": listDirections[i],
                        "next_room_id": str(listRooms[i+1])}
            except:
                # the last movement doesn't have the next room available, so when the previous payload returns error because map[i+1] doesn't exist, we just do a normal move
                payload = {"direction": listDirections[i]}
            # we move by calling the POST /move/ api endpoint with the payload
            print(f"-----Payload is: \n {payload} ------\n")
            current_room, now, cooldown = api_call_post(
                "move/", now, cooldown, payload)
            print(f"**** End of calling wise move****\n\n")
            # we set teh new cooldown based on what the new room returns us
            # cooldown = current_room["cooldown"]
            # we reset the time counter
            # now = datetime.now()
            print(f"++++We are now in room {current_room} ++++\n\n")
        roomId = current_room["room_id"]
        print(f"#### End of the trip, we are now in room {roomId} ####\n\n")
        return current_room
    else:
        return None


def collectTreasure(currentRoom):
    # we keep track of treasures collectes
    treasures = []
    # we get te list of treasures
    items = currentRoom["items"]
    print("*** We start treasure collection ***\n\n")
    # for each of the treasures
    for el in items:
        # we initialize the time
        now = datetime.now()
        # we keep track of latest cooldown
        cooldown = currentRoom["cooldown"]
        # we prepare the paylod for the api call
        payload = {"name": el}
        try:
            # we call the take endpoint
            api_call_post("take/", now, cooldown, payload)
            # we append the treasure to the list of treasures collected
            treasures.append(el)
        except:
            print(">>>> There was an error taking the treasure.. <<<< \n\n")
    # we return the treasures collected
    return treasures
