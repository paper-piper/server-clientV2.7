VALID_COMMANDS = ("exit", "update commands", "dir", "delete", "copy", "execute", "take screenshot", "send photo")


def is_valid_python_code(code):
    try:
        compile(code, '<string>', 'exec')
        return True
    except (SyntaxError, TypeError) as e:
        return False
