from util import Stack


def bfsFindTreasure(graph, visited, currentRoomId):
    s = Stack()
    # we push current room and direction we are taking
    s.push([currentRoomId])
    # we create a way to track room that have been visited
    looked = set()
    # while there is something in the Stack
    while s.size() > 0:
        # we pop the path
        path = s.pop()
        # we extract room ID and the direction that we took
        roomId = path[-1]
        # have we visited the next room?
        if roomId not in looked:
            # if we have, check how many items there are
            numbItems = len(visited[str(roomId)]["items"])
            # if there are any
            if numbItems > 0:
                # return path
                return path
            # otherwise, add the room to the looked list
            looked.add(roomId)
            # examine each exit
            for exit in graph.vertices[str(roomId)]:
                new_path = list(path)
                # new_treasure_path = list(path)
                new_path.append(graph.vertices[str(roomId)][exit])
                # we push new path to the Stack
                s.push(new_path)
    return None


def convertToSteps(rooms, graph):
    # initialise empty list for directions
    directions = []
    # we loop over the rooms path
    for i in range(len(rooms) - 1):
        # we set the next room as the target to search among connections at room[i]
        target = rooms[i+1]
        # we look for the next room among the exits of the current room
        for key, value in graph.vertices[str(rooms[i])].items():
            # if the value of one of the exits matches the target
            if value == target:
                # we append to the path of directions
                directions.append(key)
    # we retunr the list of directions
    return directions
