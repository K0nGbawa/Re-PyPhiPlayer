WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

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
