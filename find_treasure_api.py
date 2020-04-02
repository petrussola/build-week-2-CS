import time
from datetime import datetime
from api_call import api_call_post, api_call_get


def findTreasureApi(map, treasures, now, cooldown):
    for i in range(len(map)):
        # # we ceck if cooldown is over
        # then = now
        # now = datetime.now()
        # duration = now - then
        # duration_in_s = duration.total_seconds()
        # if duration_in_s <= cooldown:
        #     waiting_time = cooldown - duration_in_s
        #     print(
        #         f" >>>> Oh dear, we have to wait {waiting_time} seconds <<<<\n\n")
        #     time.sleep(waiting_time)
        #     print(f"<<<< Done with waiting. Let's move on.>>>> \n\n")
        # print(f"## Calling wise move ##\n\n")
        try:
            # we pass the direction and the next room as payload so we can avail of wise explorer cooldown reduction
            payload = {"direction": map[i][1],
                       "next_room_id": str(map[i+1][0])}
        except:
            # the last movement doesn't have the next room available, so when the previous payload returns error because map[i+1] doesn't exist, we just do a normal move
            payload = {"direction": map[i][1]}
        # we move by calling the POST /move/ api endpoint with the payload
        current_room = api_call_post(
            "move/", payload, now, cooldown)
        print(f"**** End of calling wise move****\n\n")
        # we set teh new cooldown based on what the new room returns us
        cooldown = current_room["cooldown"]
        # we reset the time counter
        now = datetime.now()
        print(f"++++We are now in room {current_room} ++++\n\n")
        # treasure collection

        roomId = current_room["room_id"]
        if treasures[i] > 0:
            print(f"#### There are {treasures[i]} treasures in room {roomId} ####\n\n")
            for _ in range(treasures[i]):
                payload_take = {
                    "name": treasures[i]
                }
                try:
                    api_call_post("take/", payload_take, now, cooldown)
                    print(f">>>> Picking up {treasures[i]} <<<<\n\n")
                except:
                    print(f">>>> There was a problem picking up {treasures[i]} <<<<\n\n")   

        print(f"There is no treasure in room {roomId}. Moving on.\n\n")
        
        # in case we don't get a room from the endpoint
        if current_room == None:
            print(f"$$$$ Something went wrong $$$$\n\n")
            break
