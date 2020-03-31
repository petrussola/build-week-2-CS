import os
import json
import requests
import random
import time
from datetime import datetime

# HELPERS
from graph import Graph
from util import Stack, Queue

# DEPENDENCIES
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("API_TOKEN")
init_api_url = os.getenv("INIT_API_URL")
move_api_url = os.getenv("MOVE_API_URL")
lenght_maze = int(os.getenv("NUM_ROOMS"), 10)

headers = {'Content-Type': 'application/json', 'Authorization': api_token}

directions = {
    "n": {"direction": 'n'},
    "s": {"direction": 's'},
    "e": {"direction": 'e'},
    "w": {"direction": 'w'},
}

# GET API CALL HELPER FUNCTION


def api_call_get(endpoint):
    print("Calling GET")
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        print("Returning GET")
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Too bad")
        return None


# POST API CALL HELPER FUNCTION
def api_call_post(endpoint, payload):
    print("Calling POST")
    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code == 200:
        print("Returning POST")
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Too bad")
        return None


# calling the init endpoint in order to get initial room
initialRoom = api_call_get(init_api_url)

# TRAVERSE GRAPH


def traverseMaze(initialRoom):
    # helper dictionary with the opposite directions when going back
    directions_opp = {
        'n': 's',
        's': 'n',
        'w': 'e',
        'e': 'w',
    }
    # We initiate a Graph
    g = Graph()
    # We initiate a Stack for rooms
    s = Stack()
    # We initiate a Stack for directions
    d = Stack()
    # We create a visited List
    visited = list()
    # Push initial room to the stack
    s.push((None, None, initialRoom))
    # while the stack has something in it
    now = datetime.now()
    while s.size() > 0:
        # if visited list is less than the number of rooms (we set the number of rooms in the env file)
        if len(visited) < lenght_maze:
            # we pull the room at the head of the stack
            prev_room, inc_dir, room = s.pop()

            # print(f"The previous room is: {prev_room}\n\n")
            # print(f"The incoming direction is: {inc_dir}\n\n")
            # print(f"The room is: {room}\n\n")

            # if the room that we pull from stack has not been visited:
            if room["room_id"] not in visited:
                # we add it to the list of visited rooms
                visited.append(room["room_id"])

            # print(f"We are in room {room.id}")
            # print(f"We have visited these rooms: {visited}")

            # if it is not in our map (Graph)
            if not room["room_id"] in g.vertices:
                # we add it to the Graph
                g.add_vertex(room["room_id"])
                # we get all the exits and add them as "?" to the map
                exits = room["exits"]
                for e in exits:
                    g.vertices[room["room_id"]][e] = "?"

            # print(f"The graph so far is: {g.vertices}\n\n")

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
                # we check if 15 sec have elapsed
                then = now
                now = datetime.now()
                duration = now - then
                duration_in_s = duration.total_seconds()
                cooldown = room["cooldown"]
                if duration_in_s <= cooldown:
                    waiting_time = cooldown - duration_in_s
                    print(f"Oh dear, we have to wait {waiting_time} seconds")
                    time.sleep(waiting_time)
                    print(f"Done with waiting. Let's move on.")
                # once cooldown has elapsed, we move in that direction calling the api move endpoint
                current_room = api_call_post(
                    move_api_url, directions[next_move])
                # we reset the cooldown timer
                now = datetime.now()
                # we add the direction to the stack of directions (ideal to go back when readching a dead end)
                d.push(next_move)
                # we add direction to traversal path
                traversal_path.append(next_move)
                # we connect the next room with the one we come from
                g.vertices[room["room_id"]
                           ][next_move] = current_room["room_id"]
                # print(g.vertices[room.id], "<< next move")
                # we add that room to the Stack for rooms
                s.push((room, next_move, current_room))

                # print(f"####Pushing####\n Room: {room}\n, Next move: {next_move}\n, Current_room: {current_room}\n\n")

            # otherwise:
            else:
                # we pop a direction from the direction Stack
                dir = d.pop()
                # we move in the opposite direction
                opp_dir = directions_opp[dir]
               # We need to wait the cooldown period in order to make the next API call.
                # we check if 15 sec have elapsed
                then = now
                now = datetime.now()
                duration = now - then
                duration_in_s = duration.total_seconds()
                cooldown = room["cooldown"]
                if duration_in_s <= cooldown:
                    waiting_time = cooldown - duration_in_s
                    print(f"Oh dear, we have to wait {waiting_time} seconds")
                    time.sleep(waiting_time)
                    print(f"Done with waiting. Let's move on.")
                current_room = api_call_post(move_api_url, directions[opp_dir])
                # we add the direction to traversal_path
                traversal_path.append(opp_dir)
                # we add the room in the Stack of rooms
                s.push((room, opp_dir, current_room))
        # otherwise
        else:
            # exit the function
            break


traversal_path = []
traverseMaze(initialRoom)
