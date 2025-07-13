import pygame
import random
import math
from settings import WIDTH

class Boss(pygame.sprite.Sprite):
    def __init__(self, image, bullet_img):
        super().__init__()
        self.image = image.copy()
        self.rect = self.image.get_rect(midtop=(WIDTH // 2, -100))
        self.health = 120
        self.max_health = 120
        self.bullet_img = bullet_img
        self.shoot_timer = 0
        self.direction = 1
        self.speed = 2
        self.entered = False

    def update(self):
        # Move boss into view, then side to side
        if not self.entered:
            self.rect.y += 2
            if self.rect.top >= 40:
                self.entered = True
        else:
            self.rect.x += self.speed * self.direction
            if self.rect.right > WIDTH - 20:
                self.direction = -1
            if self.rect.left < 20:
                self.direction = 1

            # Shooting: straight down
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot_timer = random.randint(60, 100)
                return self.shoot()
        return None

    def shoot(self):
        bullet = pygame.sprite.Sprite()
        bullet.image = self.bullet_img
        bullet.rect = bullet.image.get_rect(center=(self.rect.centerx, self.rect.bottom))
        bullet.speed = 6
        def update_bullet(self=bullet):
            self.rect.y += self.speed
        bullet.update = update_bullet
        return [bullet]

    def draw_health_bar(self, surface):
        bar_width = self.rect.width
        bar_height = 10
        x = self.rect.left
        y = self.rect.top - 16
        fill = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (200, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 220, 0), (x, y, fill, bar_height))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 2)

class Boss2(pygame.sprite.Sprite):
    def __init__(self, image, bullet_img):
        super().__init__()
        self.base_image = image.copy()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(midtop=(WIDTH // 2, -100))
        self.health = 180  # Stronger than Boss 1
        self.max_health = 180
        self.bullet_img = bullet_img
        self.shoot_timer = 0
        self.direction = 1
        self.speed = 2.5
        self.entered = False
        self.alpha = 0  # For fade-in
        self.fading_in = True

    def update(self):
        # Fade in
        if self.fading_in:
            self.alpha += 8
            if self.alpha >= 255:
                self.alpha = 255
                self.fading_in = False
            self.image = self.base_image.copy()
            self.image.set_alpha(self.alpha)
        # Move boss into view, then side to side
        if not self.entered:
            self.rect.y += 2
            if self.rect.top >= 40:
                self.entered = True
        else:
            self.rect.x += self.speed * self.direction
            if self.rect.right > WIDTH - 20:
                self.direction = -1
            if self.rect.left < 20:
                self.direction = 1

            # Shooting: circular pattern
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot_timer = random.randint(50, 80)
                return self.shoot()
        return None

    def shoot(self):
        # Fire bullets in a circle
        bullets = []
        num_bullets = 12
        for i in range(num_bullets):
            angle = 2 * math.pi * i / num_bullets
            bullet = pygame.sprite.Sprite()
            bullet.image = self.bullet_img
            bullet.rect = bullet.image.get_rect(center=self.rect.center)
            bullet.speed = 5
            bullet.dx = math.cos(angle) * bullet.speed
            bullet.dy = math.sin(angle) * bullet.speed
            def update_bullet(self=bullet):
                self.rect.x += int(self.dx)
                self.rect.y += int(self.dy)
            bullet.update = update_bullet
            bullets.append(bullet)
        return bullets

    def draw_health_bar(self, surface):
        bar_width = self.rect.width
        bar_height = 10
        x = self.rect.left
        y = self.rect.top - 16
        fill = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (200, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 220, 0), (x, y, fill, bar_height))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 2)