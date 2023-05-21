#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from CNEngine import *
from os import devnull
from os.path import isfile
from pygame.mixer import music
from random import randint
from threading import Thread
from time import sleep

font.init()

HELP = """USAGE:
    ./badapple.py (-h) (--no-debug) (--no-thread) (-m [music_path]) (-p [frames_path]) (-f [frame amount])
DESCRIPTION:
    a program made for the 2023 Epitech jam by Steven Gandon and Yamao Cuzou.
"""
colors = [
    (255, 255,  255),
    (0, 0, 0)
]
frame_number = 8762
frames = [None for _ in range(0, frame_number)]
bars = '|/-\\'
TEXTS = [
    "She turned her back to the sun, and learned to trust the path\nof her shadow.",
    "I bit into his candy-coated heart, to find his core was rotten."
]
ASCII_CHARS = '.",:;!~+-xmo*#W&8@'
ASCII_COEFF = 255 // (len(ASCII_CHARS))
ASCII_FONT = font.SysFont('Courier', 12, bold=True)
RENDERED = [ASCII_FONT.render(item, False, (255, 255, 255 )) for item in reversed(ASCII_CHARS)]

class PixelText(Text):
    def __init__(self: object, x: int, y: int, B, text: str = '', color: tuple = (255, 255, 255), font: object = None, split_newline=True) -> None:
        super().__init__(x, y, text, color, font, split_newline)
        self.B = B

    def draw(self, screen):
        if (self.B.params["pixel"]):
            super().draw(screen)

class ScrollBar(EmptyHud):
    def __init__(self: object, x: int, y: int, size_x: int, size_y: int, callback, B) -> None:
        super().__init__(x, y)
        self.size_x = size_x
        self.B = B
        self.size_y = size_y
        self.rect = Rect(self.draw_x, self.draw_y, self.size_x, self.size_y)
        self.rect2 = Rect(self.draw_x, self.draw_y, 10, self.size_y)
        self.callback = callback
        self.font = font.SysFont("Consola", 35)
        self.bar = 0

    def event(self, event):
        if (not self.B.params["pixel"]):
            return
        m_x, m_y = mouse.get_pos()

        if (m_x < self.draw_x or m_x > self.x+self.size_x) or (m_y < self.draw_y or m_y > self.y+self.size_y):
            return

        if mouse.get_pressed()[0]:
            self.callback(m_x - self.draw_x)
            self.bar = m_x - self.draw_x

    def update(self, parent):
        if (self.B.params["pixel"]):
            super().update(parent)

    def draw(self, screen):
        if (self.B.params["pixel"]):
            draw.rect(screen, colors[0], self.rect)
            self.rect2.left = self.bar + self.draw_x - self.rect2.width / 2
            draw.rect(screen, colors[1], self.rect2)
            render = self.font.render(str(self.B.pixelization), 0, colors[0])
            screen.blit(render, (self.draw_x + self.size_x + 10, self.draw_y + 5), render.get_rect())
        

class ButtonWhite(Button):
    def __init__(self: object, x: int, y: int, size_x: int, size_y: int, callback=None) -> None:
        super().__init__(x, y, size_x, size_y, callback)
        self.rect = Rect(x, y, size_x, size_y)
        self.selected = False

    def update(self, parent):
        if (self.clicked):
            self.selected = not self.selected 
        super().update(parent)

    def draw(self, screen):
        draw.rect(screen, colors[0], self.rect)
        if (self.selected):
            draw.line(screen, colors[1], (self.draw_x, self.draw_y), (self.draw_x + self.size_x, self.draw_y + self.size_y), 3)
            draw.line(screen, colors[1], (self.draw_x, self.draw_y + self.size_y), (self.draw_x + self.size_x, self.draw_y), 3)

class ButtonWhitePixel(Button):
    def __init__(self: object, x: int, y: int, size_x: int, size_y: int, B, callback=None) -> None:
        super().__init__(x, y, size_x, size_y, callback)
        self.rect = Rect(x, y, size_x, size_y)
        self.selected = False
        self.B = B

    def event(self, event):
        if (self.B.params["pixel"]):
            super().event(event)

    def update(self, parent):
        if (not self.B.params["pixel"]):
            return
        if (self.clicked):
            self.selected = not self.selected 
        super().update(parent)

    def draw(self, screen):
        if (self.B.params["pixel"]):
            draw.rect(screen, colors[0], self.rect)
            if (self.selected):
                draw.line(screen, colors[1], (self.draw_x, self.draw_y), (self.draw_x + self.size_x, self.draw_y + self.size_y), 3)
                draw.line(screen, colors[1], (self.draw_x, self.draw_y + self.size_y), (self.draw_x + self.size_x, self.draw_y), 3)

class BadApple(Tile):
    def __init__(self: object, x: int, y: int, G, sprite: object, grid_size: int = 16, pixel_size: int = 3, z: int = 0, no_music = 0) -> None:
        self.frame = 0
        self.params = {
            "inv_x": False,
            "inv_y": False,
            "inv_c": False,
            "pixel": False,
            "un_pixelate": False,
            "re_pixelate": False,
            "sort_pixel": False,
            "ascii": False
        }
        self.timeout = 50000
        sleep(0.1)
        self.sprite = frames[self.frame]
        if (not no_music):
            music.play()
        self.no_music = no_music
        self.G = G

        super().__init__(x, y, self.sprite, grid_size, pixel_size, z)
        self.draw_x = x
        self.draw_y = y
        self.time = 0
        self.pixelization = 2

    def change_pixelate(self: object, x):
        self.pixelization = 2 + x

    def show_ascii(self: object, img, screen):
        img = img.copy()
        width = img.get_width()
        height = img.get_height()
        step = int(0.6 * 12)

        pixel_array = PixelArray(img)

        for x in range(0, width, step):
            for y in range(0, height, step):
                index = (pixel_array[x, y] >> 16) & 0xFF // ASCII_COEFF
                if index < 18:
                    screen.blit(RENDERED[index], (x, y))

        pixel_array.close()

    def inverse_frame_y(self: object):
        self.sprite = self.sprite.copy()
        self.sprite = transform.flip(self.sprite, 0, 1)

    def inverse_frame_x(self: object):
        self.sprite = self.sprite.copy()
        self.sprite = transform.flip(self.sprite, 1, 0)

    def update(self: object, parent: object) -> None:
        timeout = 0
    
        if (self.params["un_pixelate"] and self.params["pixel"] and not self.params["re_pixelate"]):
            self.time += 1
            if (self.time > 15):
                if (self.pixelization < 212):
                    self.pixelization += 1
                self.time = 0

        if (self.params["re_pixelate"] and self.params["pixel"] and not self.params["un_pixelate"]):
            self.time += 1
            if (self.time > 15):
                if (self.pixelization > 2):
                    self.pixelization -= 1
                self.time = 0

        if self.frame == frame_number - 1:
            self.frame = -1
            if (not self.no_music):
                music.play()

        self.frame += 1
        while (frames[self.frame] == None and timeout < self.timeout):
            timeout += 1
        self.sprite = frames[self.frame]

    def sort_pixel(self, img):
        img = img.copy()
        width = img.get_width()
        height = img.get_height()

        pixel_array = PixelArray(img)

        for x in range(width):
            for y in range(height - 1):
                for j in range(y + 1, height):
                    if (pixel_array[x, y] < pixel_array[x, j]):
                        pixel_array[x, j], pixel_array[x, y] = pixel_array[x, y], pixel_array[x, j]

        pixel_array.close()
        return (img)

    def inverted(self: object, img):
        inv = Surface(img.get_rect().size, SRCALPHA)
        inv.fill((255,255,255,255))
        inv.blit(img, (0,0), None, BLEND_RGB_SUB)
        return inv
    
    def event(self, event):
        if (event.type ==  KEYDOWN and event.key == K_a):
            self.G.size = ((800, 360) if self.G.size != (800, 360) else (480, 360))
            display.set_mode(self.G.size)
        return super().event(event)

    def draw(self: object, screen: str, cam_x: int, cam_y: int):
        if (self.params["inv_x"]):
            self.inverse_frame_x()
        if (self.params["inv_y"]):
            self.inverse_frame_y()
        if (self.params["inv_c"]):
            self.sprite = self.inverted(self.sprite)
        if (self.params["pixel"]):
            self.sprite = transform.scale(self.sprite, (self.pixelization, self.pixelization))
        if (self.params["sort_pixel"] and self.params["pixel"]):
            self.sprite = self.sort_pixel(self.sprite)
        if (self.params["ascii"]):
            self.show_ascii(self.sprite, screen)
        else:
            super().draw(screen, cam_x, cam_y)

class Haiku(TextBox):
    def __init__(self, x, y, background=None, text='', color=(0, 0, 0), font=None, text_margin=(0, 0, 0, 0), split_newline=True, size_x=None, size_y=None, scrollable=False):
        super().__init__(x, y, background, text, color, font, text_margin, split_newline, size_x, size_y, scrollable)
        self.rect = Rect(self.draw_x, self.draw_y, 400, 100)
        self.tex = 0

    def update(self: object, parent: object) -> None:
        self.tex += 1
        if (self.tex > 200):
            self.tex = 0
            self.set_text(TEXTS[randint(0, len(TEXTS) - 1)])
        return super().update(parent)

    def draw(self, screen):
        draw.rect(screen, colors[0], self.rect)
        super().draw(screen)

def load_images(frame_number, folder):
    invalid = 0

    print("[*] Loading frame ...\b\b\b", end='', flush=True)
    for i in range(0, frame_number):
        print(f"[{i + 1}/{frame_number}] {bars[i % 4]}" + '\b' * (len(str(i + 1)) + len(str(frame_number)) + 5), end='', flush=True)
        try:
            if (not isfile(f"{folder}/frame{i}.jpg")):
                invalid += 1
                continue
            frames[i] = image.load(f"{folder}/frame{i}.jpg").convert()

        except Exception as e:
            print(e)
            invalid += 1

    print("Done!          ")
    print(f"[*] File successfully loaded: {frame_number - invalid}/{frame_number} ({invalid} frames are missing)")

def change_param_inv_x(B):
    B.params["inv_x"] = not B.params["inv_x"]

def change_param_inv_y(B):
    B.params["inv_y"] = not B.params["inv_y"]

def change_param_inv_c(B, G):
    global RENDERED

    colors.reverse()
    G.color = (colors[1])

    for item in G.hud:
        if (type(item).__name__ in ("Text", "PixelText")):
            item.set_color(colors[0])
        if (type(item).__name__ in ("Haiku",)):
            item.set_color(colors[1])

    B.params["inv_c"] = not B.params["inv_c"]
    RENDERED = [ASCII_FONT.render(item, False, colors[0]) for item in reversed(ASCII_CHARS)]

def progressive_pixelization(B):
    B.params["re_pixelate"] = not B.params["re_pixelate"]

def progressive_unpixelization(B):
    B.params["un_pixelate"] = not B.params["un_pixelate"]

def change_param_pixel(B):
    B.params["pixel"] = not B.params["pixel"]

def change_param_sort_pixel(B):
    B.params["sort_pixel"] = not B.params["sort_pixel"]

def change_param_ascii(B):
    B.params["ascii"] = not B.params["ascii"]

def load_scene(G, music_file, no_music):
    if (not no_music):
        music.load(music_file)

    C = Camera(0,0,12)
    B = BadApple(0,0, G,None,0,1, 11, no_music)
    add_camera_to_game(G, C)

    P = Player(G.size[0]/2-16, G.size[1]/2-16, None, z = 11)
    MyText = Text(0,0,"none", font=font.SysFont("Consolas", 12))

    add_object_to_game(G, P)

    add_object_to_game(G, B)
    add_hud_to_game(G, Haiku(480, 340, font=font.SysFont("Consola", 16)))
    #add_hud_to_game(G, MyText)
    add_hud_to_game(G, ButtonWhite(490, 10, 35, 35, lambda: change_param_inv_x(B)))
    add_hud_to_game(G, ButtonWhite(490, 55, 35, 35, lambda: change_param_inv_y(B)))
    add_hud_to_game(G, ButtonWhite(490, 100, 35, 35, lambda: change_param_inv_c(B, G)))
    add_hud_to_game(G, ButtonWhite(490, 145, 35, 35, lambda: change_param_pixel(B)))
    add_hud_to_game(G, ButtonWhitePixel(490, 235, 35, 35, B, lambda: progressive_pixelization(B)))
    add_hud_to_game(G, ButtonWhitePixel(535, 235, 35, 35, B, lambda: progressive_unpixelization(B)))
    add_hud_to_game(G, ButtonWhitePixel(490, 280, 35, 35, B, lambda: change_param_sort_pixel(B)))
    add_hud_to_game(G, ButtonWhite(650, 10, 35, 35, lambda: change_param_ascii(B)))
    add_hud_to_game(G, ButtonWhite(650, 55, 35, 35, lambda: music.set_volume(0 if music.get_volume() != 0 else 1)))
    
    add_hud_to_game(G, PixelText(590, 247, B, "Progressive Pixelization", (255, 255, 255), font.SysFont("Consola", 22)))
    add_hud_to_game(G, PixelText(545, 292, B, "Sort Pixels", (255, 255, 255), font.SysFont("Consola", 22)))
    add_hud_to_game(G, Text(545, 22, "FlipX", (255, 255, 255), font.SysFont("Consola", 22)))
    add_hud_to_game(G, Text(545, 67, "FlipY", (255, 255, 255), font.SysFont("Consola", 22)))
    add_hud_to_game(G, Text(545, 112, "Inverse Color", (255, 255, 255), font.SysFont("Consola", 22)))
    add_hud_to_game(G, Text(545, 157, "Pixelate", (255, 255, 255), font.SysFont("Consola", 22)))
    add_hud_to_game(G, Text(705, 22, "Ascii", (255, 255, 255), font.SysFont("Consola", 22)))
    add_hud_to_game(G, Text(705, 67, "Mute", (255, 255, 255), font.SysFont("Consola", 22)))
    add_hud_to_game(G, ScrollBar(490, 190, 210, 35, lambda x: B.change_pixelate(x), B))

    add_script_to_game(G, lambda *args: show_fps(MyText, G))

    #add_action_to_player(P, lambda p,k: k[K_z], PLAYER_MOVE_UP)
    #add_action_to_player(P, lambda p,k: k[K_s], PLAYER_MOVE_DOWN)
    #add_action_to_player(P, lambda p,k: k[K_q], PLAYER_MOVE_LEFT)
    #add_action_to_player(P, lambda p,k: k[K_d], PLAYER_MOVE_RIGHT)

    #add_action_to_player(P, lambda p,k: k[K_z], lambda p: C.move(C.x, C.y - p.force, C.z))
    #add_action_to_player(P, lambda p,k: k[K_s], lambda p: C.move(C.x, C.y + p.force, C.z))
    #add_action_to_player(P, lambda p,k: k[K_d], lambda p: C.move(C.x + p.force, C.y, C.z))
    #add_action_to_player(P, lambda p,k: k[K_q], lambda p: C.move(C.x - p.force, C.y, C.z))

def main(args: list) -> int:
    exit_status = 0
    no_music = 0

    if ("-h" in args):
        print(HELP)
        return 0

    if ("--no-debug" in args):
        sys.stdout = open(devnull, 'w')

    print("[*] Initing engine...\b\b\b", end='', flush=False)
    init_engine()
    print(" Done!")

    if ("-f" in args):
        if (args.index("-f") +  1 >= len(args) or not args[args.index("-f") +  1].isnumeric()):
            print("[-] Invalid arguments after -f")
            return (1)
        global frame_number
        global frames
        frame_number = int(args[args.index("-f") +  1])
        print("[*] Realocating frame buffer...\b\b\b", end='', flush=True)
        frames = [None for _ in range(frame_number)]
        print(" Done!")

    if ("-p" in args):
        if (args.index("-p") + 1 >= len(args)):
            print("[-] Invalid arguments after -p")
            return (1)
        path = args[args.index("-p") +  1]
    else:
        path = "datas/images/frames"

    if ("-m" in args):
        if (args.index("-m") + 1 >= len(args)):
            print("[-] Invalid arguments after -m")
            return (1)
        music_file = args[args.index("-m") +  1]
        if (not isfile(music_file)):
            no_music = 1
            print("[!] Music file not found")
    else:
        music_file = "./bad-apple.mp3"

    G = create_game("Bad Apple", (480,360), 0, 41, False, (0,0,0))

    if ("--no-thread" in args):
        load_images(frame_number, path)
    else:
        print("[*] Starting thread 1.")
        T = Thread(target=lambda: load_images(frame_number, path), daemon=True)
        T.start()

    load_scene(G, music_file, no_music)

    try:
        G.run()
    except KeyboardInterrupt:
        print("[*] Sigint received aborting.")
        exit_status = 130

    if ("--no-thread" not in args):
        print("[*] Closing threads.")
        T.join(-1)
    if ("--no-debug" in args):
        sys.stdout.close()
        sys.stdout = sys.__stdout__

    return (exit_status)

if __name__ == '__main__':
    exit(main(argv))
