import os
import json
import requests
from graph import Graph
from player import Player
from dotenv import load_dotenv

load_dotenv()


api_token = os.getenv("API_TOKEN")
init_api_url = os.getenv("INIT_API_URL")

headers = {'Content-Type': 'application/json', 'Authorization': api_token}

directions = {
    "n": {"direction": 'n'},
    "s": {"direction": 's'},
    "e": {"direction": 'e'},
    "w": {"direction": 'w'},
}


def api_call(endpoint):
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


get_info = api_call(init_api_url)
print(get_info)


# TRAVERSE GRAPH
def traverseMaze(initialRoom):
    directions = {
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
    while s.size() > 0:
        # if visited list is less than the number of rooms
        if len(visited) < len(room_graph):
            # we pull the room at the head of the stack
            prev_room, inc_dir, room = s.pop()
            # if the room that we pull from stack has not been visited:
            if room.id not in visited:
                # we add it to the list of visited rooms
                visited.append(room.id)
            # print(f"We are in room {room.id}")
            # print(f"We have visited these rooms: {visited}")
            # if it is not in our map (Graph)
            if not room.id in g.vertices:
                # we add it to the Graph
                g.add_vertex(room.id)
                # we get all the exits and add them as "?" to the map
                exits = room.get_exits()
                for e in exits:
                    g.vertices[room.id][e] = "?"
            # if we are not in the initial room
            # print(g.vertices[room.id])
            if inc_dir != None:
                # connect current room with the previous room
                g.vertices[room.id][directions[inc_dir]] = prev_room.id
            # we pick one with ? at random
            av_exits = []
            for e in g.vertices[room.id]:
                if g.vertices[room.id][e] == "?":
                    av_exits.append(e)
            if len(av_exits) > 0:
                next_move = random.choice(av_exits)
                # we move in that direction
                player.travel(next_move)
                current_room = player.current_room
                # we add the direction to the stack of directions
                d.push(next_move)
                # we add direction to traversal path
                traversal_path.append(next_move)
                # we connect the next room with the one we come from
                g.vertices[room.id][next_move] = current_room.id
                # print(g.vertices[room.id], "<< next move")
                # we add that room to the Stack for rooms
                s.push((room, next_move, current_room))
            # otherwise:
            else:
                # we pop a direction from the direction Stack
                dir = d.pop()
                # we move in the opposite direction
                opp_dir = directions[dir]
                player.travel(opp_dir)
                current_room = player.current_room
                # we add the room in the Stack of rooms
                traversal_path.append(opp_dir)
                s.push((room, opp_dir, current_room))
        # otherwise
        else:
            # exit the function
            break
