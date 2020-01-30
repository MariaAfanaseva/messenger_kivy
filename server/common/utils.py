import json
from common.variables import ENCODING, MAX_PACKAGE_LENGTH
from common.errors import IncorrectDataNotDictError
from common.decos import Logging


@Logging()
def send_msg(socket, msg):
    json_msg = json.dumps(msg)
    coding_msg = json_msg.encode(ENCODING)
    socket.send(coding_msg)


def get_msg(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise IncorrectDataNotDictError
