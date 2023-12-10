"""
Author: Yoni Reichert
Program name: Mini-Command-Server
Description: Listens for commands and sends back dynamic responses.
Date: 06-11-2023
"""

import base64
import binascii
import glob
import socket
import logging
import os
import shutil
import subprocess
import pyautogui
import time

# need to change dir re return parsed list (look nice)

MAX_PACKET = 1024
QUEUE_LEN = 1
SERVER_ADDRESS = ('0.0.0.0', 1729)

IMAGE_PATH = 'screen.jpg'
MESSAGE_SEPARATOR = "!"

# Set up logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('server')

# assert consistent
my_script_path = "file_writer.exe"
folder_path = 'asserts_folder'
file_path = f"{folder_path}/test.txt"
copied_file_path = f"{folder_path}/copied_test.txt"
FILE_CONTENTS = "Hello!"
executed_conformation = "Executed"


def process_request(msg_type, msg_cont):
    """
    process client's command into server's response
    :param msg_type:
    :param msg_cont:
    :return:
    """
    response = None
    try:
        match msg_type:
            case 1:
                response = dir_cmd(msg_cont)
            case 2:
                delete_cmd(msg_cont)
            case 3:
                copy_cmd(msg_cont.split(" ")[0], msg_cont.split(" ")[1])
            case 4:
                execute_cmd(msg_cont)
            case 5:
                take_screenshot_cmd()
            case 6:
                image_bytes = send_photo_cmd()
                response = base64.b64encode(image_bytes).decode('utf-8')
            # continue for all cases
            case _:
                logger.error("Client sent unknown word")
                response = "You sent an unknown command, try again or type 'exit' to exit"
        if response is None:
            response = "0"
    except Exception as e:
        logger.error(f"Server Failed to create a response, ({e})")
        response = "-1"
    finally:
        response = str(len(response)) + MESSAGE_SEPARATOR + str(msg_type) + response
        return response


def parse_message(sock):
    """
    Receives messages from the server.
    :param sock:
    :return:
    Messages protocol:
    [message content length]![message type][message content]
    """
    len_str = ""
    while True:
        char = sock.recv(1).decode()
        if not char:  # Empty string indicates client disconnection
            raise ConnectionError("Client disconnected")
        if char == MESSAGE_SEPARATOR:
            break
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
        msg_type, msg_cont = parse_message(client_socket)
        # check if client exited
        if msg_type == 0:
            client_socket.close()
            return
        response = process_request(msg_type, msg_cont)
        if response is not None:
            client_socket.send(response.encode())


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


def dir_cmd(path) -> str:
    """
    return string of all files in a folder
    :param path:
    :return:
    """
    if not os.path.exists(path):
        logger.error("User entered invalid path")
        raise ValueError("The specified path does not exist.")
    items = glob.glob(os.path.join(path, "*.*"))
    formatted_items = ['- ' + os.path.basename(item) for item in items]
    return '\n'.join(formatted_items)


def delete_cmd(path):
    """
    delete file in specific path
    :param path:
    :return:
    """
    os.remove(path)


def copy_cmd(copy_from, copy_to):
    """
    copy one file content to another
    :param copy_from:
    :param copy_to:
    :return:
    """
    shutil.copy(copy_from, copy_to)


def execute_cmd(path):
    """
    execute the program in the specified path
    :param path:
    :return:
    """
    subprocess.call(path)


def take_screenshot_cmd():
    """
    take a screenshot and save it in IMAGE PATH
    :return:
    """
    image = pyautogui.screenshot()
    image.save(IMAGE_PATH)


def send_photo_cmd() -> bytes:
    """
    get the screenshot to the client
    :return image bytes:
    """
    with open(IMAGE_PATH, 'rb') as photo:
        image_bytes = photo.read()
    return image_bytes


if __name__ == "__main__":
    # checking all the server's functions
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(file_path, 'w') as file:
            file.write(FILE_CONTENTS)
        copy_cmd(file_path, copied_file_path)
        assert os.path.exists(copied_file_path)
        assert dir_cmd(folder_path).count('\n') + 1 == 2  # we add one because the first line doesn't have \n

        # this .exe writes "Executed" to the file
        execute_cmd(my_script_path)
        with open(file_path, 'r') as file:
            file_content = file.read()
            assert file_content == executed_conformation

        # checking send photo, screenshot, and delete functions
        if os.path.exists(IMAGE_PATH):
            delete_cmd(IMAGE_PATH)
        take_screenshot_cmd()
        assert send_photo_cmd() is not None
        delete_cmd(IMAGE_PATH)

        # cleaning up the folder
        shutil.rmtree(folder_path)
    except (OSError, binascii.Error):
        raise AssertionError("Assertion gone wrong")
    main()

