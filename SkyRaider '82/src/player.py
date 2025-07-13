import pygame
from settings import PLAYER_SPEED

class Player(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(400, 550))
        self.shoot_cooldown = 0

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += PLAYER_SPEED
        self.rect.x += dx
        self.rect.y += dy
        # Keep player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, 800, 600))
