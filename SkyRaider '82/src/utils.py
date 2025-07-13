import pygame

def load_image(path):
    return pygame.image.load(path).convert_alpha()

def load_sound(path):
    return pygame.mixer.Sound(path)

def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)
