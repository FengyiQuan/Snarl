import socket


def flatten_2d_list(list_2d):
    return [y for x in list_2d for y in x]


def switch_xy_coordinate(pos: tuple):
    assert len(pos) == 2
    return pos[1], pos[0]


def print_map_score(score_map: map):
    res = ''
    for key, value in score_map.items():
        res += key + ': ' + str(value) + ' '
    return res


def send_msg(sock: socket.SocketType, msg: str) -> None:
    print('send >> ', msg)
    sock.sendall(msg.encode())


def receive_msg(sock: socket.SocketType) -> str:
    data = sock.recv(4096)
    if not data:
        return data

    response = data.decode()
    print('receive << ', response)
    return response
