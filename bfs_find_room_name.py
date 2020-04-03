from util import Stack


def findRoom(graph, visited, startingRoom, roomName):
    startingRoomId = startingRoom["room_id"]
    s = Stack()
    s.push([startingRoomId])
    looked = set()
    while s.size() > 0:
        path = s.pop()
        roomId = path[-1]
        if roomId not in looked:
            if visited[str(roomId)]["title"] == roomName:
                return path
            looked.add(roomId)
            for exit in graph.vertices[str(roomId)]:
                new_path = list(path)
                new_path.append(graph.vertices[str(roomId)][exit])
                s.push(new_path)
    return None
