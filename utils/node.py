import bpy


def set_socket_value_range(socket: bpy.types.NodeSocket,
                           default_value: float = 0.0,
                           min_value: float = 0.0,
                           max_value: float = 1.0) -> None:
    assert socket.type == "VALUE"

    socket.default_value = default_value
    socket.min_value = min_value
    socket.max_value = max_value
