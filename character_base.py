# character_base.py
import pygame
from setting import *

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, team):
        super().__init__()
        self.team = team # "PLAYER" atau "ENEMY"
        
        # Status Dasar (Akan di-override oleh class spesifik)
        self.hp = 100
        self.max_hp = 100
        self.attack_power = 10
        self.speed = 5
        self.attack_speed = 1.0 
        
        # Tampilan Default (Bentuk kotak sementara sebelum ada aset gambar)
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE if team == "PLAYER" else RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, dx, dy):
        """Logika pergerakan dasar"""
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def action_melee(self):
        # Tombol F
        print(f"[{self.team}] Melakukan serangan Melee dasar!")

    def action_ranged(self):
        # Tombol G
        print(f"[{self.team}] Menembakkan serangan Ranged dasar!")

    def action_defense(self):
        # Tombol H
        print(f"[{self.team}] Bertahan!")

    def action_ultimate(self):
        # Tombol J
        print(f"[{self.team}] Menggunakan Ultimate dasar!")

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.die()

    def die(self):
        print("Karakter mati!")
        self.kill()