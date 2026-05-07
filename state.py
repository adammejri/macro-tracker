location = []

def push(name):
    location.append(name)

def pop():
    if location:
        location.pop()

def where():
    if not location:
        return "Main Menu"
    return " > ".join(location)

def reset():
    location.clear()

def check_global(command):
    if command.strip().lower() == "where":
        print(f"Current location: {where()}")
        return True
    return False