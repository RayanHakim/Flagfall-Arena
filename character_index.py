import pygame
from setting import *
from character_assassin import Assassin
from character_knight import Knight
from character_tank import Tank
from character_wizard import Wizard
from character_support import Support

class CharacterIndexScreen:
    def __init__(self, font_title, font_subtitle):
        self.font_title = font_title
        self.font_subtitle = font_subtitle
        self.font_desc = pygame.font.SysFont('trebuchetms', 28)
        self.font_info = pygame.font.SysFont('trebuchetms', 22)
        
        self.current_idx = 0
        
        # Inisialisasi Karakter Preview
        self.previews = [
            Assassin(0, 0, "PLAYER"),
            Knight(0, 0, "PLAYER"),
            Tank(0, 0, "PLAYER"),
            Wizard(0, 0, "PLAYER"),
            Support(0, 0, "PLAYER")
        ]
        
        self.classes_data = [
            {
                "name": "THE ASSASSIN",
                "color": YELLOW,
                "lore": "Seorang pembunuh bayaran yang bergerak dalam bayang-bayang. Memiliki kecepatan luar biasa namun pertahanan yang sangat rapuh.",
                "stats": "HP: 70 | ATK: 25 | SPD: 8.0",
                "skills": "[F] Shadow Slash: Tebasan pedang super cepat.\n[G] Throwing Knife: Serangan jarak jauh ringan.\n[H] Stealth: Menghilang sejenak dari pandangan.\n[J] Shadow Dash: Berpindah tempat secara instan."
            },
            {
                "name": "THE KNIGHT",
                "color": (200, 200, 200),
                "lore": "Ksatria kerajaan yang kokoh dengan zirah baja. Penyeimbang antara daya tahan dan kekuatan serangan di garda depan.",
                "stats": "HP: 150 | ATK: 15 | SPD: 4.5",
                "skills": "[F] Broadsword: Tebasan pedang berat.\n[G] Shield Toss: Melempar perisai ke arah musuh.\n[H] Shield Wall: Bertahan total dari damage.\n[J] Brave Charge: Menerjang musuh dengan brutal."
            },
            {
                "name": "THE TANK",
                "color": (160, 100, 50),
                "lore": "Benteng berjalan yang hampir tidak bisa dihancurkan. Menggunakan palu godam untuk menggetarkan bumi.",
                "stats": "HP: 300 | ATK: 10 | SPD: 2.5",
                "skills": "[F] Hammer Slam: Menghantam tanah di depan.\n[G] Rock Throw: Melempar batu besar ke musuh.\n[H] Fortify: Menjadi tak tergoyahkan (Immune).\n[J] Earthshatter: Shockwave masif di area luas."
            },
            {
                "name": "THE WIZARD",
                "color": (150, 50, 255),
                "lore": "Penguasa elemen dari menara sihir. Menyerang dari jarak jauh dengan kekuatan sihir tingkat tinggi.",
                "stats": "HP: 80 | ATK: 20 | SPD: 4.0",
                "skills": "[F] Magic Staff: Pukulan tongkat jarak dekat.\n[G] Fireball: Tembakan energi api beruntun.\n[H] Blink: Teleportasi jarak pendek.\n[J] Meteor Strike: Hujan api dahsyat dari langit."
            },
            {
                "name": "THE SUPPORT",
                "color": (0, 255, 255),
                "lore": "Penyembuh mistis yang fokus utama menjaga kawan tetap hidup dengan aura penyembuhan suci.",
                "stats": "HP: 100 | ATK: 8 | SPD: 5.0",
                "skills": "[F] Staff Poke: Serangan ringan jarak dekat.\n[G] Light Orb: Menembakkan bola cahaya suci.\n[H] Protective Aura: Membuat tameng energi tim.\n[J] Area Healing: Memulihkan HP diri dan kawan."
            }
        ]

    def draw_text_shadow(self, screen, text, font, color, x, y, center=False):
        shadow = font.render(text, True, BLACK)
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        screen.blit(shadow, (rect.x + 3, rect.y + 3))
        screen.blit(surf, rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.current_idx = (self.current_idx - 1) % len(self.classes_data)
            elif event.key == pygame.K_RIGHT:
                self.current_idx = (self.current_idx + 1) % len(self.classes_data)

    def draw(self, screen):
        data = self.classes_data[self.current_idx]
        char = self.previews[self.current_idx]
        
        # Background Dinamis
        screen.fill((15, 15, 20))
        bg_glow = pygame.Surface((WIDTH, HEIGHT))
        bg_glow.fill(data["color"])
        bg_glow.set_alpha(15)
        screen.blit(bg_glow, (0,0))
        
        # Judul
        self.draw_text_shadow(screen, "CHARACTER INDEX", self.font_title, WHITE, WIDTH//2, 60, center=True)
        
        # Update dan Gambar Karakter Preview
        char.state = "IDLE"
        char.draw_shape()
        
        big_char = pygame.transform.scale(char.image, (400, 400))
        char_rect = big_char.get_rect(center=(WIDTH//2 - 250, HEIGHT//2 + 50))
        
        # Efek Cahaya
        pygame.draw.ellipse(screen, (data["color"][0], data["color"][1], data["color"][2], 40), 
                           (char_rect.centerx - 150, char_rect.bottom - 50, 300, 60))
        screen.blit(big_char, char_rect)
        
        # Panel Informasi
        info_rect = pygame.Rect(WIDTH//2 + 50, 150, 520, 480) # Dibuat sedikit lebih tinggi
        pygame.draw.rect(screen, (30, 35, 45), info_rect, border_radius=20)
        pygame.draw.rect(screen, data["color"], info_rect, 3, border_radius=20)
        
        self.draw_text_shadow(screen, data["name"], self.font_subtitle, data["color"], info_rect.x + 30, info_rect.y + 30)
        self.draw_text_shadow(screen, data["stats"], self.font_desc, WHITE, info_rect.x + 30, info_rect.y + 85)
        
        pygame.draw.line(screen, (80, 80, 80), (info_rect.x + 30, info_rect.y + 135), (info_rect.right - 30, info_rect.y + 135), 2)
        
        # Word Wrap Lore
        words = data["lore"].split(' ')
        lines = []
        curr = ""
        for w in words:
            if len(curr + w) < 38: curr += w + " "
            else:
                lines.append(curr)
                curr = w + " "
        lines.append(curr)
        
        for i, line in enumerate(lines):
            l_surf = self.font_info.render(line, True, (220, 220, 220))
            screen.blit(l_surf, (info_rect.x + 30, info_rect.y + 155 + (i * 28)))
            
        # Abilities Section (Lengkap F, G, H, J)
        self.draw_text_shadow(screen, "ABILITIES:", self.font_info, data["color"], info_rect.x + 30, info_rect.y + 270)
        for i, line in enumerate(data["skills"].split('\n')):
            s_surf = self.font_info.render(line, True, WHITE)
            screen.blit(s_surf, (info_rect.x + 30, info_rect.y + 305 + (i * 35)))

        # Navigasi UI
        self.draw_text_shadow(screen, "< [LEFT]", self.font_desc, (100, 100, 100), 50, HEIGHT//2, center=False)
        self.draw_text_shadow(screen, "[RIGHT] >", self.font_desc, (100, 100, 100), WIDTH - 180, HEIGHT//2, center=False)
        
        nav_hint = f"Hero {self.current_idx + 1} of {len(self.classes_data)} | Press [BACK] to Menu"
        self.draw_text_shadow(screen, nav_hint, self.font_info, (120, 120, 120), WIDTH//2, HEIGHT - 40, center=True)