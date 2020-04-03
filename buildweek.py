import os
import json
import requests
import random
import time
from datetime import datetime

# HELPERS
from graph import Graph
from util import Stack, Queue
from find_treasure_api import findSomethingApi, collectTreasure
from bfs_find_treasure import bfsFindTreasure, convertToSteps
from bfs_find_room_name import findRoom
from api_call import api_call_post, api_call_get_timer

# DEPENDENCIES
from dotenv import load_dotenv

load_dotenv()

# file to cache Graph
# graph_file = open("graph.txt", "w")
# visited_file = open("visited.txt", "w")

api_token = os.getenv("API_TOKEN")
init_api_url = os.getenv("INIT_API_URL")
move_api_url = os.getenv("MOVE_API_URL")
lenght_maze = int(os.getenv("NUM_ROOMS"), 10)
base_api_url = os.getenv("BASE_API_URL")

headers = {'Content-Type': 'application/json', 'Authorization': api_token}

directions = {
    "n": {"direction": 'n'},
    "s": {"direction": 's'},
    "e": {"direction": 'e'},
    "w": {"direction": 'w'},
}

# GET API CALL HELPER FUNCTION


def api_call_get(endpoint):
    # print("Calling GET\n")
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        # print("Returning GET\n")
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Too bad\n")
        return None


# POST API CALL HELPER FUNCTION
def api_call_post_initial(endpoint, payload):
    # print("Calling POST\n")
    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code == 200:
        # print("Returning POST\n")
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Too bad\n")
        print(json.loads(response.content.decode('utf-8')))
        return None


# calling the init endpoint in order to get initial room
initialRoom = api_call_get(init_api_url)

# TRAVERSE GRAPH


def traverseMaze(initialRoom, graph_file, visited_file):
    # helper dictionary with the opposite directions when going back
    directions_opp = {
        'n': 's',
        's': 'n',
        'w': 'e',
        'e': 'w',
    }
    # We initiate a Graph
    g = Graph()
    # we load cache of data from text file
    try:
        # in case there is data
        g.vertices = json.load(graph_file)
    except:
        # in case text file is empty
        g.vertices = {}
    # We initiate a Stack for rooms
    s = Stack()
    # We initiate a Stack for directions
    d = Stack()
    # We create a visited List
    try:
        # in case there is data
        visited = json.load(visited_file)
    except:
        # in case text file is empty
        visited = {}
    # Push initial room to the stack
    try:
        # we handle last room file
        lastRoomFile = open("last_room.txt", "r")
        lastRoomVisited = json.load(lastRoomFile)

        # we handle last direction file
        lastDirectionFile = open("last_direction.txt", "r")
        lastDirectionTaken = json.load(lastDirectionFile)
        oppositeDirection = directions_opp[lastDirectionTaken]

        previousRoomId = g.vertices[str(
            lastRoomVisited["room_id"])][oppositeDirection]
        previousRoom = visited[str(previousRoomId)]

        s.push((previousRoom, lastDirectionTaken, lastRoomVisited))
        # we close the files
        lastRoomFile.close()
        lastDirectionFile.close()
    except:
        print("Didn't have data from last_room.txt file")
        s.push((None, None, initialRoom))
    # we keep track of the latest cooldown period. We initialise the variable to 15 seconds to keep track of it.
    cooldown = int(os.getenv("DEFAULT_COOLDOWN"), 10)
    now = datetime.now()
    # while the stack has something in it
    while s.size() > 0:
        print(f"The stack is {len(s.stack)} long: \n\n")
        # if visited list is less than the number of rooms (we set the number of rooms in the env file)
        if len(visited) < lenght_maze:
            # we pull the room at the head of the stack
            prev_room, inc_dir, room = s.pop()

            # we record the last room we have been in
            lastRoomFile = open("last_room.txt", "w")
            lastRoomVisited = json.dumps(room)
            lastRoomFile.write(lastRoomVisited)
            lastRoomFile.close()

            # we record the last direction we have taken
            lastDirectionFile = open("last_direction.txt", "w")
            lastDirectionTaken = json.dumps(inc_dir)
            lastDirectionFile.write(lastDirectionTaken)
            lastDirectionFile.close()

            # if the room that we pull from stack has not been visited:
            if room["room_id"] not in visited:
                # we add it to the list of visited rooms
                visited[room["room_id"]] = room

            # if it is not in our map (Graph)
            if not room["room_id"] in g.vertices:
                # we add it to the Graph
                g.add_vertex(room["room_id"])
                # we get all the exits and add them as "?" to the map
                exits = room["exits"]
                for e in exits:
                    g.vertices[room["room_id"]][e] = "?"

            # if we are not in the initial room (because initial room has inc_dir = None)
            if inc_dir != None:
                # connect current room with the previous room
                g.vertices[room["room_id"]][directions_opp[inc_dir]
                                            ] = prev_room["room_id"]
            # we build a list of directions that have not been explored yet (have "?" in our map)
            av_exits = []
            for e in g.vertices[room["room_id"]]:
                if g.vertices[room["room_id"]][e] == "?":
                    av_exits.append(e)
            # if there are unexplored directions
            if len(av_exits) > 0:
                # we choose one direction at random
                next_move = random.choice(av_exits)
                # We need to wait the cooldown period in order to make the next API call.
                then = now
                now = datetime.now()
                duration = now - then
                duration_in_s = duration.total_seconds()
                # we check if 15 sec have elapsed
                if duration_in_s <= cooldown:
                    waiting_time = cooldown - duration_in_s
                    print(f"Oh dear, we have to wait {waiting_time} seconds")
                    time.sleep(waiting_time)
                    print(f"Done with waiting. Let's move on.")
                # once cooldown has elapsed, we move in that direction calling the api move endpoint
                current_room = api_call_post_initial(
                    move_api_url, directions[next_move])
                # we reset the cooldown timer
                cooldown = current_room["cooldown"]
                now = datetime.now()
                # we add the direction to the stack of directions (ideal to go back when readching a dead end)
                d.push(next_move)
                # we add direction to traversal path
                traversal_path.append(next_move)
                # we connect the next room with the one we come from
                g.vertices[room["room_id"]
                           ][next_move] = current_room["room_id"]
                # we add that room to the Stack for rooms
                s.push((room, next_move, current_room))
                # we cache the graph so far into the graph.txt file
                graph_so_far = json.dumps(g.vertices)
                # we open the file
                graph_file = open("graph.txt", "w")
                # write graph so far in the file
                graph_file.write(graph_so_far)
                # close graph file
                graph_file.close()
                # we cache the visited dict with every room information so far into the txt file
                visited_so_far = json.dumps(visited)
                # we open the file
                visited_file = open("visited.txt", "w")
                # write visited so far in the file
                visited_file.write(visited_so_far)
                # close visited file
                visited_file.close()
            # otherwise:
            else:
                # we pop a direction from the direction Stack
                dir = d.pop()
                # we move in the opposite direction
                opp_dir = directions_opp[dir]
               # We need to wait the cooldown period in order to make the next API call.
                then = now
                now = datetime.now()
                duration = now - then
                duration_in_s = duration.total_seconds()
                # we check if 15 sec have elapsed
                if duration_in_s <= cooldown:
                    waiting_time = cooldown - duration_in_s
                    print(f"Oh dear, we have to wait {waiting_time} seconds")
                    time.sleep(waiting_time)
                    print(f"Done with waiting. Let's move on.")
                current_room = api_call_post_initial(
                    move_api_url, directions[opp_dir])
                # we reset the cooldown timer
                cooldown = current_room["cooldown"]
                now = datetime.now()
                # we add the direction to traversal_path
                traversal_path.append(opp_dir)
                # we add the room in the Stack of rooms
                s.push((room, opp_dir, current_room))
                # we cache the graph so far into the graph.txt file
                graph_so_far = json.dumps(g.vertices)
                # we open the file
                graph_file = open("graph.txt", "w")
                # write graph so far in the file
                graph_file.write(graph_so_far)
                # close graph file
                graph_file.close()
                # we cache the visited dict with every room information so far into the txt file
                visited_so_far = json.dumps(visited)
                # we open the file
                visited_file = open("visited.txt", "w")
                # write visited so far in the file
                visited_file.write(visited_so_far)
                # close visited file
                visited_file.close()
        # otherwise
        else:
            # exit the function
            break


traversal_path = []
graph_file = open("graph.txt", "r")
visited_file = open("visited.txt", "r")

# traverseMaze(initialRoom, graph_file, visited_file)

# SEARCH FOR TREASURE

# import the map we built previously after traversing the maze
# initialize a Graph
g = Graph()
# back up it up with the Graph of the maze
g.vertices = json.load(graph_file)
# initialize the inventory of rooms
visited = {}
# back it up with the inventory of rooms done while traversing the graph
visited = json.load(visited_file)
# get the id of the initial room
startingRoomId = initialRoom["room_id"]
###### traverse the graph until we find 1000 gold #####
# get an initial random direction to get started
nextDirection = random.choice(initialRoom["exits"])
# initialize list to keep track of rooms where we found treasure, so local map is synched with server map
roomsTreasure = list()
now = datetime.now()
cooldown = initialRoom["cooldown"]
# check initial status of player
status, now, cooldown = api_call_post("status/", now, cooldown, {})
# now = datetime.now()
# cooldown = status["cooldown"]

######################################################
##### FIND TREASURE, SHOP, SELL AND COLLECT GOLD #####
######################################################


# while status["gold"] < 1000:
#     print(f"==============\n STARTING NEW TREASURE HUNT\n============== \n")
#     ##############
#     ## TREASURE ##
#     ##############
#     # find the path of rooms to the nearest treasure
#     path = bfsFindTreasure(g, visited, initialRoom["room_id"], roomsTreasure)
#     # add last room in the path, the one with the treasure, to the roomsTreasure list
#     roomsTreasure.append(path[-1])
#     print(f"#### PATH TO TREASURE: ####\n {path}")
#     # convert the path of rooms to directions
#     pathDirections = convertToSteps(path, g)
#     print(f"#### DIRECTIONS TO TREASURE: ####\n {pathDirections}")
#     # convert the path of rooms and directions into real movements inside the maze. Returns the room containing treasure.
#     currentRoom = findSomethingApi(path, pathDirections, now, cooldown)
#     # collect all treasures in the room
#     if currentRoom is not None:
#         print(f"Current room is NOT None")
#         treasuresCollected = collectTreasure(currentRoom)
#         now = datetime.now()
#         cooldown = currentRoom["cooldown"]
#         print(f"!!!!Cooldown is:!!!!\n {cooldown}\n")
#     else:
#         print(f"Current room is None")
#         initRoom = api_call_get_timer("init/", now, cooldown)
#         treasuresCollected = collectTreasure(initRoom)
#         now = datetime.now()
#         cooldown = initRoom["cooldown"]
#         print(f"----Cooldown is:----\n {cooldown}\n")
#     print(
#     f"####We have collected these treasures: ####\n {treasuresCollected}")
#     status, now, cooldown = api_call_post("status/", now, cooldown, {})
#     print(f"$$$$Status: $$$$ {status}")
#     # now = datetime.now()
#     # cooldown = status["cooldown"]
#     itemsInventory = status["inventory"]
#     print(f"&&& We have collected these treasures: &&&\n {itemsInventory}\n")

#     if len(treasuresCollected) > 0:
#         ##########
#         ## SHOP ##
#         ##########
#         print(f"==============\n STARTING SHOP HUNT\n============== \n")
#         # find path to the shop
#         pathShop = findRoom(g, visited, currentRoom, "Shop")
#         #######
#         ####### ^^^^^ for debugging, change initialRoom with currentRoom and viceversa
#         #######
#         print(f"#### PATH TO SHOP: ####\n\n {pathShop}")
#         # convert shop path into steps
#         pathDirectionsShop = convertToSteps(pathShop, g)
#         print(f"#### DIRECTIONS TO SHOP: ####\n\n {pathDirectionsShop}")
#         # move in the server map
#         shop = findSomethingApi(pathShop, pathDirectionsShop, now, cooldown)
#         now = datetime.now()
#         cooldown = shop["cooldown"]

#         ############################
#         ## CHECK NUMBER TREASURES ##
#         ############################

#         print(f"==============\n CHECHING STATUS\n============== \n")
#         status, now, cooldown = api_call_post("status/", now, cooldown, {})
#         treasures = status["inventory"]
#         gold = status["gold"]
#         print(f"++++You have now these treasures:++++\n {treasures}\n")
#         print(f"****You have this gold:****\n {gold}\n")
#         # now = datetime.now()
#         # cooldown = status["cooldown"]

#         #######################
#         ## SALE OF TREASURES ##
#         #######################

#         print(f"==============\n START SALE OF TREASURES\n============== \n")
#         inventory = status["inventory"]
#         print(f"You have this much gold in your pocket:\n {inventory}")
#         for el in status["inventory"]:
#             try:
#                 payload = {
#                     "name": el
#                 }
#                 print(f"Payload to sell, starting: {payload}\n")
#                 answer, now, cooldown = api_call_post('sell/', now, cooldown, payload)
#                 print(f"Cooldown: {cooldown}")
#                 print(f"Now: {now}")
#                 message = answer["messages"]
#                 print(f"Answer: {message}")
#                 print(f">>>The shop keeper tells you:\n {message}\n <<<")
#                 print(f"Sale finished\n")
#                 # now = datetime.now()
#                 # cooldown = answer["cooldown"]
#                 print(f"==============\n SALE COMPLETED> STARTING CONFIRMATION\n============== \n")
#                 if len(answer["messages"]) > 0:
#                     payload = {
#                         "name": el,
#                         "confirm": "yes"
#                     }
#                     try:
#                         print(f"Payload to confirm sale, starting: {payload}\n")
#                         answer, now, cooldown = api_call_post("sell/", now, cooldown, payload)
#                         print(f"Confirm sale finished\n")
#                     except:
#                         print(">>>> There was a problem confirming the sale. <<<<\n\n")
#             except:
#                 print(">>>> There was a problem selling the treasure. <<<<\n\n")
#             status, now, cooldown = api_call_post("status/", now, cooldown, {})
#             treasures = status["inventory"]
#             gold = status["gold"]
#             print(f"++++You have now these treasures:++++\n {treasures}\n")
#             print(f"****You have this gold:****\n {gold}\n")
#             # now = datetime.now()
#             # cooldown = shop["cooldown"]
#             print(f"==============\n SALE CONFIRMED\n============== \n")
#     else:
#         print(f"Hmmm, there were no treasures after all, continue hunting..\n")
#         print(f"==============\n GETTING NEW INITIAL ROOM\n============== \n")
#         initialRoom = api_call_get_timer("init/", now, cooldown)
#         now = datetime.now()
#         cooldown = initialRoom["cooldown"]
#         print(f"££££ Initial room is now: ££££\n {initialRoom}\n")

#############################################################
##### END OF FIND TREASURE, SHOP, SELL AND COLLECT GOLD #####
#############################################################

#############################################################
##### START OF FINDING NAME ROOM #####
#############################################################
# # get the current room
# currentRoom, now, cooldown = api_call_get_timer("init/", now, cooldown)

# # find path to the shop
# pathName = findRoom(g, visited, currentRoom, "Pirate Ry's")
# #######
# # ^^^^^ for debugging, change initialRoom with currentRoom and viceversa
# #######
# print(f"#### PATH TO NAME CHANGER: ####\n\n {pathName}")
# # convert shop path into steps
# pathDirectionsName = convertToSteps(pathName, g)
# print(f"#### DIRECTIONS TO NAME CHANGER: ####\n\n {pathDirectionsName}")
# # move in the server map
# name = findSomethingApi(pathName, pathDirectionsName, now, cooldown)
# currentRoom, now, cooldown = api_call_get_timer("init/", now, cooldown)
# print(f"Here we are, in the name changer room:\n {currentRoom}")
# # change name
# response = api_call_post('change_name/', now, cooldown,
#                          {"name": "Pere Sola Claver", 'confirm': 'aye'})
# print(f"We get this as a response:\n {response}\n")
#############################################################
##### END OF FINDING NAME ROOM AND CHANGING ROOM      #####
#############################################################

#############################################################
##### START OF FINDING SHRINE AND PRAYING      #####
#############################################################
# # get the current room
# currentRoom, now, cooldown = api_call_get_timer("init/", now, cooldown)

# # find path to the shop
# pathShrine = findRoom(g, visited, currentRoom, "The Peak of Mt. Holloway")
# #######
# # ^^^^^ for debugging, change initialRoom with currentRoom and viceversa
# #######
# print(f"#### PATH TO SHRINE: ####\n\n {pathShrine}")
# # convert shop path into steps
# pathDirectionsShrine = convertToSteps(pathShrine, g)
# print(f"#### DIRECTIONS TO SHRINE: ####\n\n {pathDirectionsShrine}")
# # move in the server map
# name = findSomethingApi(pathShrine, pathDirectionsShrine, now, cooldown)
# currentRoom, now, cooldown = api_call_get_timer("init/", now, cooldown)
# print(f"Here we are, in the SHRINE:\n {currentRoom}")
# # pray
# response = api_call_post('pray/', now, cooldown,
#                          {})
# print(f"We get this as a response after praying:\n {response}\n")

#############################################################
##### END OF FINDING SHRINE AND PRAYING      #####
#############################################################

#############################################################
##### START OF FINDING WISHING WELL      #####
#############################################################
# # get the current room
# currentRoom, now, cooldown = api_call_get_timer("init/", now, cooldown)

# # find path to the shop
# pathWell = findRoom(g, visited, currentRoom, "Wishing Well")
# #######
# # ^^^^^ for debugging, change initialRoom with currentRoom and viceversa
# #######
# print(f"#### PATH TO SHRINE: ####\n\n {pathWell}")
# # convert shop path into steps
# pathDirectionsWell = convertToSteps(pathWell, g)
# print(f"#### DIRECTIONS TO WELL: ####\n\n {pathDirectionsWell}")
# # move in the server map
# well, now, cooldown = findSomethingApi(pathWell, pathDirectionsWell, now, cooldown)
# currentRoom, now, cooldown = api_call_get_timer("init/", now, cooldown)
# print(f"Here we are, in the WELL:\n {currentRoom}")
# # # pray
# # response = api_call_post('pray/', now, cooldown,
# #                          {})
# # print(f"We get this as a response after praying:\n {response}\n")
#############################################################
##### END OF FINDING WISHING WELL      #####
#############################################################

#############################################################
##### START OF EXAMINING WISHING WELL                   #####
#############################################################
# get the current room
currentRoom, now, cooldown = api_call_get_timer("init/", now, cooldown)

# examine well
response, now, cooldown = api_call_post('examine/', now, cooldown,
                         {"name": "well"})
print(f"We get this as a response after examining well:\n {response}\n")
code = response["description"].split("...")[1]
binCode = code.split("\n")[2:]
f = open("machine_code.txt", "a+")
for c in binCode:
    print(c, "<<<<<<<<<<<<<<<<<")
    f.write(f"{c}\n")
f.close()
# print(code)

#############################################################
##### END OF EXAMINING WISHING WELL                     #####
#############################################################