"""
Author: Yoni Reichert
Program name: Mini-Command-Server
Description: Listens for commands and sends back dynamic responses.
Date: 06-11-2023
"""

import socket
import logging
import importlib
import ServerCommands


MAX_PACKET = 1024
QUEUE_LEN = 1
SERVER_ADDRESS = ('0.0.0.0', 1729)

IMAGE_PATH = 'screen.jpg'
COMMANDS_FILE_PATH = "ServerCommands.py"

# set up logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('server')

MESSAGE_SEPARATOR = "!"
SUCCESS_CHAR = "0"
FAIL_CHAR = "-1"
UPDATE_SERVER_CMD = 1


def update_commands_file(new_commands_content):
    # since client is responsible for checking the validation of the code, the server doesn't need to
    try:
        with open(COMMANDS_FILE_PATH, 'a') as commands_file:
            commands_file.write(new_commands_content)
        importlib.reload(ServerCommands)
        logger.info(f"Successfully updated '{COMMANDS_FILE_PATH}' with content from the new client's content.")
    except Exception as e:
        print(f"An error occurred: {e}")


def process_request(cmd_type, cmd_cont):
    """
    process client's command into server's response
    :param cmd_type:
    :param cmd_cont:
    :return:
    """
    # check if the request is to update the server
    if cmd_type == UPDATE_SERVER_CMD:
        update_commands_file(cmd_cont)
        return SUCCESS_CHAR

    cmd_content = None
    try:
        cmd = getattr(ServerCommands, ServerCommands.VALID_COMMANDS[cmd_type] + "_cmd")
        if cmd_cont is None or cmd_cont == "":
            cmd_content = cmd()
        else:
            cmd_content = cmd(cmd_cont)
    except Exception as e:
        logger.error(f"Failed while trying to processed command: {ServerCommands.VALID_COMMANDS[cmd_type]}. Error: {e}")
        cmd_content = FAIL_CHAR.encode()
    finally:
        return cmd_content


def send_message(sock, msg_cont, cmd_id):
    """
    parse according to protocol and send message to server
    :param sock: Socket
    :param msg_cont:
    :param cmd_id:
    :return:
    """
    # [content len]![cmd id][content]
    if msg_cont is None:
        message = "1".encode() + MESSAGE_SEPARATOR.encode() + cmd_id.encode() + SUCCESS_CHAR.encode()
    else:
        message = str(len(msg_cont)).encode() + MESSAGE_SEPARATOR.encode() + cmd_id.encode() + msg_cont
    sock.send(message)
    return


def parse_message(sock):
    """
    Receives messages from the server.
    :param sock:
    :return:
    Messages protocol:
    since message type is fixed (0-9) a separation symbol is not required
    [message content length]![message type][message content]
    0. Exit
    1. ...

    """
    # since client is responsible for validation of message, the server doesn't need to check
    len_str = ""
    while (char := sock.recv(1).decode()) != MESSAGE_SEPARATOR:
        len_str += char
    msg_len = int(len_str)
    msg_type = int(sock.recv(1).decode())
    msg_content = sock.recv(msg_len).decode()
    return msg_type, msg_content


def handle_client_messages(client_socket):
    """
    Handle client messages until 'exit' command is received.
    also contains all the function for the different server commands
    @:param client_socket: The socket object associated with the client.
    @:return: None
    @:raises: socket error if there's an error in receiving data.
    """
    while True:
        cmd_id, request_cont = parse_message(client_socket)
        # check if client exited
        if cmd_id == 0:
            client_socket.close()
            return
        cmd_content = process_request(cmd_id, request_cont)
        send_message(client_socket, cmd_content, str(cmd_id))


def accept_client(server_socket):
    """
    accept client and get his messages until disconnected
    :param server_socket:
    :return:
    """
    client_socket, client_address = server_socket.accept()
    try:
        logger.info(f"Accepted connection from {client_address[0]}: {client_address[1]}")
        handle_client_messages(client_socket)
    except socket.error as err:
        logger.error('Received error while handling client: %s', err)
        client_socket.close()


def main():
    """
    Initialize the server socket, accept incoming connections, and handle messages.
    @:return: None
    @:raises: socket error on socket-related errors, KeyboardInterrupt when user interrupts the process.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Starting server
        server_socket.bind(SERVER_ADDRESS)
        server_socket.listen(QUEUE_LEN)
        logger.info(f"Server is listening on {SERVER_ADDRESS[0]}: {SERVER_ADDRESS[1]}")
        # listen to clients forever
        while True:
            accept_client(server_socket)
    except socket.error as err:
        logger.error('Received socket error on server socket: %s', err)
    except KeyboardInterrupt:
        logger.info("Server was terminated by the user.")
    finally:
        server_socket.close()
        logger.info("Server socket closed.")


if __name__ == "__main__":
    # Make new assertion checks

    main()
