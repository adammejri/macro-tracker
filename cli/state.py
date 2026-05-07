_location = []

def push(name):
    _location.append(name)

def pop():
    if _location:
        _location.pop()

def where():
    if not _location:
        return "Main Menu"
    return " > ".join(_location)

def reset():
    _location.clear()

def check_global(command):
    stripped = command.strip().lower()
    if stripped == "where":
        print(f"Current location: {where()}")
        return True
    if stripped == "commands":
        return "commands"
    return False