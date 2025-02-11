import json, zipfile, yaml, typing, io

from const import *
from PIL import Image

def parse_info_csv(s:str) -> dict:
    result_list = [item.split(",") for item in s.replace("\r", "").split("\n")]
    return {k: result_list[2][i] for i, k in enumerate(result_list[0])}

def parse_info_txt(s:str) -> dict:
    result_list = [item.split(": ", maxsplit=1) for item in s.replace("\ufeff", "").replace("\r", "").split("\n") if item and item.strip() != "#"]
    return {k: v for k, v in result_list}

def put_info_values(to: "Chart", info: dict[str, str], keymaps:dict[str, str] = None, default: typing.Optional[dict[str, str]] = None):
    info = (default.copy() if default is not None else {}) | info
    to.name = info.get(keymaps["name"], "UK")
    to.level = info.get(keymaps["level"], "UK  Lv.10")
    to.composer = info.get(keymaps["composer"], "UK")
    to.illustrator = info.get(keymaps["illustrator"], "UK")
    to.chart_path = info.get(keymaps["chart"], None)
    to.music_path = info.get(keymaps["music"], None)
    to.bg_path = info.get(keymaps["illustration"], None)

def get_info(fp: zipfile.ZipFile, to: "Chart"):
    if "info.yml" in fp.namelist():
        info = yaml.safe_load(fp.read("info.yml").decode())
        put_info_values(to, info, KEYMAPS["info.yml"])
    elif "info.txt" in fp.namelist():
        info = parse_info_txt(fp.read("info.txt").decode())
        put_info_values(to, info, KEYMAPS["info.txt"])
    elif "info.csv" in fp.namelist():
        info = parse_info_csv(fp.read("info.csv").decode())
        put_info_values(to, info, KEYMAPS["info.csv"])
    else:
        put_info_values(to, {}, KEYMAPS["info.yml"])

def get_resouce(fp: zipfile.ZipFile, end:tuple[str]=(".json", ".pec"), path: typing.Optional[str]=None, tip=GET_RESOURCE_DEFAULT_TIP) -> bytes:
    try:
        return fp.read(path)
    except KeyError:
        namelist = [name for name in fp.namelist() if name.lower().endswith(end)]
        if len(namelist) == 1:
            return fp.read(namelist[0])
        elif len(namelist) > 1:
            print(tip)
            for i, name in enumerate(namelist):
                print(f"{i} {name}")
            print()
            while True:
                select = input(f"{" "*100}\r")
                try:
                    return fp.read(namelist[int(select)])
                except (IndexError, ValueError) as e:
                    print(f"{" "*100}\r{RED}{e}{RESET}\033[1A\r", end="")

class Chart:
    name: str
    level: str
    composer: str
    illustrator: str
    chart_path: str
    music_path: str
    bg_path: str
    chart: dict
    music: bytes
    bg: Image.Image
    bg_io: io.BytesIO

    def __init__(self, path: str):
        self.chart_path = None
        self.bg_path = None
        self.music_path = None
        with zipfile.ZipFile(path, "r") as f:
            get_info(f, self)
            self.chart = json.loads(get_resouce(f, path=self.chart_path).decode())
            self.music = get_resouce(f, path=self.music_path, end=(".wav", ".ogg", ".mp3", ".flac"), tip=GET_RESOURCE_TIP % ("音乐", "背景音乐"))
            self.bg_io = io.BytesIO(get_resouce(f, path=self.bg_path, end=(".png", ".jpg", ".jpeg"), tip=GET_RESOURCE_TIP % ("图片", "背景")))
            self.bg = Image.open(self.bg_io)
        if "META" in self.chart:
            self.format = ["RPE", self.chart["META"]["RPEVersion"]]
        elif "formatVersion" in self.chart:
            self.format = ["Phi", self.chart["formatVersion"]]
        else:
            raise ValueError("Unknown format")

    def __repr__(self):
        return f"<Chart name={self.name}, level={self.level}, format={self.format}>"
