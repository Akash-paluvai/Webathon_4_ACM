from main import app
with open("routes_list.txt", "w") as f:
    for route in app.routes:
        if hasattr(route, 'path'):
            f.write(f"Path: {route.path}, Methods: {route.methods}\n")
