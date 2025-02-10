import pygame

from PIL import Image
from io import BytesIO
from dataclasses import dataclass
from OpenGL.GL import *

@dataclass
class Texture:
    texture_id: int
    width: int
    height: int

    @classmethod
    def from_bytes(cls, data) -> "Texture":
        with BytesIO(data) as bytesio:
            return cls.from_path(bytesio)

    @classmethod
    def from_bytes_with_wh(cls, mode, data, w, h) -> "Texture":
        with Image.frombytes(mode, (w, h), data) as img:
            return cls.from_image(img)

    @classmethod
    def from_path(cls, path) -> "Texture":
        with Image.open(path) as img:
            return cls.from_image(img)
    
    @classmethod
    def from_image(cls, img) -> "Texture":
        img = img.convert("RGBA").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        return cls(texture_id, img.width, img.height)
    
    def set_width(self, x):
        self.width = x
        return self

    def set_height(self, x):
        self.height = x
        return self