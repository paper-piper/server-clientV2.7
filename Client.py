"""
Author: Yoni Reichert
Program name: Mini-Command-Client
Description: Sends commands and displays server responses.
Date: 06-11-2023
"""
import socket
import logging
from PIL import Image
import io
import ClientCommands

MAX_PACKET = 1024
SERVER_ADDRESS = ('127.0.0.1', 1729)

# Set up logging
logging.basicConfig(filename='client.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('client')

MESSAGE_SEPARATOR = "!"


def parse_response(sock):
    """
    receives message from server and parses it
    :param sock:
    :return:
    Messages structure:
    [cont_len]![cmd_type][cmd_cont]
    """
    try:
        len_str = ""
        while (char := sock.recv(1).decode()) != MESSAGE_SEPARATOR:
            len_str += char
        msg_len = int(len_str)
        msg_type = int(sock.recv(1).decode())
        msg_content = sock.recv(msg_len)
        return msg_type, msg_content
    except Exception as e:
        logger.error("Failed to parse message")


def handle_response(response_type, response_cont):
    """
    Handles the server response according to type
    :param response_type:
    :param response_cont:
    :return: None
    """
    # check if message failed

    # need to find a way how to not crash and not execute if the command failed.
    # if response_cont.decode() == "-1":
    #     print(f"Operation {VALID_COMMANDS[response_type]} failed")

    match response_type:
        case 2: # dir
            print(response_cont)
        case 7: # send photo
            image = Image.open(io.BytesIO(response_cont))
            # Display the image
            image.show()
        case _:
            if response_cont.decode() == "0":
                print(f"Operation {ClientCommands.VALID_COMMANDS[response_type]} was successful")

    # Need to create functions for each response type
    return


def send_message(msg_cont, msg_type, sock):
    """
    parse according to protocol and send message to server
    :param msg_cont:
    :param msg_type:
    :param sock:
    :return:
    """
    message = str(len(msg_cont)) + MESSAGE_SEPARATOR + msg_type + msg_cont
    sock.send(message.encode())
    return


def validate_user_input(message):
    """
    Validate the client's message against expected commands.
    @:param message: The message string to validate.
    @:return: True if message is valid, False otherwise.
    """
    for command in ClientCommands.VALID_COMMANDS:
        if message.startswith(command):
            return True
    # if message doesn't match any command, return un-valid
    logger.info(f"User tried to enter un-valid command, ({message})")
    return False


def parse_user_input(user_input):
    """
    parse user input into command type and command content
    :param user_input:
    :return: command type
    :return: command content
    """
    for command in ClientCommands.VALID_COMMANDS:
        if user_input.startswith(command + " "):
            return str(ClientCommands.VALID_COMMANDS.index(command)), user_input[len(command):].strip()
        elif user_input == command:  # Check for commands without additional content
            return str(ClientCommands.VALID_COMMANDS.index(command)), ""
    # don't need to check for invalid input, since we already checked that


def send_messages_loop(client_socket):
    """
    send a message to the server and print response
    :param client_socket:
    :return:
    """
    try:
        print("Choose one of the following commands:")
        for cmd in ClientCommands.VALID_COMMANDS:
            print(f"{cmd}, ", end="")
        print("")
        while True:
            message = input("Enter message: ")
            if message == 'exit':
                return
            # validate message
            if validate_user_input(message):
                msg_type, msg_content = parse_user_input(message)
                if msg_type == ClientCommands.VALID_COMMANDS.index("update commands"):
                    # check client code validation
                    pass

                send_message(msg_content, msg_type, client_socket)
                # response_cont here is bytes, not string
                response_type, response_cont = parse_response(client_socket)
                handle_response(response_type, response_cont)
            else:
                print("You entered an un-valid message, try again or type 'exit' to exit")
    except socket.error as err:
        logger.error('Received socket error: %s', err)


def main():
    """
    Connect to the server socket, send messages, and receive responses.
    @:return: None
    @:raises: socket error on socket-related errors.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(SERVER_ADDRESS)
        logger.info(f"Managed to connect to the server at: {SERVER_ADDRESS}")
        send_messages_loop(client_socket)
    except socket.error as err:
        logger.error('Received socket error: %s', err)
    finally:
        client_socket.close()
        logger.info("Client socket closed.")


if __name__ == "__main__":
    main()
