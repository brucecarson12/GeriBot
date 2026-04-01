import os


def ensure_temp_dir() -> str:
    path = os.path.join(os.getcwd(), "temp")
    os.makedirs(path, exist_ok=True)
    return path
