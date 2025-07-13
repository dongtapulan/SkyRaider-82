import pygame
import math
import random
from settings import ENEMY_SPEED

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.move_type = 'zigzag' if random.random() < 0.7 else 'straight'  # Only zigzag or straight

    def update(self):
        if self.move_type == 'zigzag':
            self.rect.x += int(5 * math.sin(pygame.time.get_ticks() / 200))
        self.rect.y += ENEMY_SPEED  # Always move down

        # Do NOT use self.shoot_timer here!

class Enemy2(Enemy):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
        self.speed_multiplier = 1.4
        self.shoot_timer = random.randint(40, 80)
        self.move_type = 'zigzag' if random.random() < 0.7 else 'straight'

    def update(self):
        if self.move_type == 'zigzag':
            self.rect.x += int(7 * math.sin(pygame.time.get_ticks() / 180))
        self.rect.y += int(ENEMY_SPEED * self.speed_multiplier)
        # Shooting logic...
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(40, 80)
            self.shoot()

    def shoot(self):
        from bullet import EnemyBullet
        offset = 12
        left_bullet = EnemyBullet(self.rect.centerx - offset, self.rect.bottom)
        right_bullet = EnemyBullet(self.rect.centerx + offset, self.rect.bottom)
        if hasattr(self, 'enemy_bullet_group'):
            self.enemy_bullet_group.add(left_bullet, right_bullet)

class Enemy3(Enemy):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)
        self.move_type = 'straight'
        self.speed_multiplier = 1.7  # Increase this value for more speed

    def update(self):
        self.rect.y += int(ENEMY_SPEED * self.speed_multiplier)
        if self.rect.top > 800:  # Or use HEIGHT
            self.kill()
