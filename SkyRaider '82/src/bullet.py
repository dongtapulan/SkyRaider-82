import pygame
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.speed = -10
        self.angle = 0  # Default: straight up

    def update(self):
        # Move bullet with angle if set
        if self.angle != 0:
            rad = math.radians(self.angle)
            self.rect.x += int(10 * math.sin(rad))
            self.rect.y += int(self.speed * math.cos(rad))
        else:
            self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += 7
        if self.rect.top > 600:
            self.kill()
