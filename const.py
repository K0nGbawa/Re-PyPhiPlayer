import sys
from tkinter.filedialog import askopenfilename

def get_value(name, default):
    try:
        index = sys.argv.index(f"--{name}")
        return sys.argv[index+1]
    except ValueError:
        return default

WINDOW_SIZE = [int(i) for i in get_value("size", "800x600").split("x")]
WINDOW_WIDTH = WINDOW_SIZE[0]
WINDOW_HEIGHT = WINDOW_SIZE[1]

RED: str = "\033[91m"
GREEN: str = "\033[92m"
YELLOW: str = "\033[93m"
BLUE: str = "\033[94m"
MAGENTA: str = "\033[95m"
CYAN: str = "\033[96m"
WHITE: str = "\033[97m"
RESET: str = "\033[0m"

KEYMAPS = {
    "info.yml": {
        "name": "name",
        "level": "level",
        "composer": "composer",
        "illustrator": "illustrator",
        "chart": "chart",
        "music": "music",
        "illustration": "illustration"
    },
    "info.txt": {
        "name": "Name",
        "level": "Level",
        "composer": "Composer",
        "illustrator": "Illustrator",
        "chart": "Chart",
        "music": "Song",
        "illustration": "Illustration"
    },
    "info.csv": {
        "name": "Name",
        "level": "Level",
        "composer": "Designer",
        "illustrator": "Illustrator",
        "chart": "Chart",
        "music": "Music",
        "illustration": "Image"
    }
}

GET_RESOURCE_DEFAULT_TIP = "在压缩包中找到了多个谱面，请选择一个："
GET_RESOURCE_TIP = "在压缩包中找到了多个%s，请选择一个作为%s："

config = {
    "chart": get_value("chart", askopenfilename(title="选择谱面", filetypes=[("谱面文件", ["*.pez", "*.zip"]), ("所有文件", "*.*")]))
}