import pygame
import sys
import random
from setting import *

from map_forest import MapForest
from map_desert import MapDesert
from map_ice import MapIce

from character_assassin import Assassin
from character_knight import Knight
from character_tank import Tank
from character_wizard import Wizard
from character_support import Support

from character_index import CharacterIndexScreen
from mechanism import FlagManager, AIController, CombatManager, MatchManager, SpawnManager

class Button:
    def __init__(self, x, y, width, height, text, font_size=35, bg_color=(40, 45, 60), hover_color=(70, 130, 180)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont('trebuchetms', font_size, bold=True)
        self.color_normal = bg_color
        self.color_hover = hover_color
        self.is_hovered = False

    def draw(self, screen):
        color = self.color_hover if self.is_hovered else self.color_normal
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8) 
        
        text_shadow = self.font.render(self.text, True, BLACK)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2)) 
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered

class NumberSpinner:
    def __init__(self, x, y, label, start_val=0):
        self.x, self.y = x, y
        self.label = label
        self.value = start_val
        self.font = pygame.font.SysFont('trebuchetms', 25, bold=True)
        
        self.btn_min = Button(x + 120, y, 30, 30, "-", 25, (150, 50, 50), (200, 80, 80))
        self.btn_plus = Button(x + 190, y, 30, 30, "+", 25, (50, 150, 50), (80, 200, 80))

    def draw(self, screen):
        lbl_surf = self.font.render(self.label, True, (200, 200, 200))
        screen.blit(lbl_surf, (self.x, self.y + 5))
        val_surf = self.font.render(str(self.value), True, WHITE)
        screen.blit(val_surf, (self.x + 165, self.y + 5))
        
        self.btn_min.draw(screen)
        self.btn_plus.draw(screen)

    def handle_event(self, event, mouse_pos, max_val=5, min_val=0):
        self.btn_min.check_hover(mouse_pos)
        self.btn_plus.check_hover(mouse_pos)
        
        if self.btn_plus.is_clicked(event):
            if self.value < max_val: self.value += 1
        elif self.btn_min.is_clicked(event):
            if self.value > min_val: self.value -= 1

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y, team):
        super().__init__()
        self.team = team
        self.carrier = None
        self.image = pygame.Surface((40, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (120, 80, 40), (5, 0, 8, 100))
        color = (0, 100, 255) if team == "BLUE" else (255, 50, 0)
        pygame.draw.polygon(self.image, color, [(13, 5), (38, 25), (13, 45)])
        self.rect = self.image.get_rect(center=(x, y))

class FlagfallArena:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # Inisialisasi Audio Engine
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flagfall Arena")
        self.clock = pygame.time.Clock()
        
        self.state = "MENU" 
        
        self.font_title = pygame.font.SysFont('impact', 110)
        self.font_subtitle = pygame.font.SysFont('trebuchetms', 40, bold=True)
        self.font_score = pygame.font.SysFont('impact', 60)
        
        self.index_screen = CharacterIndexScreen(self.font_title, self.font_subtitle)
        
        self.maps = ["Map: Forest", "Map: Desert", "Map: Ice"]
        self.sel_map_idx = 0
        self.mc_classes = ["Assassin", "Knight", "Tank", "Wizard", "Support"]
        self.sel_mc_idx = 0
        
        self.camera_x = 0
        self.camera_y = 0
        self.bots = []
        self.world_sprites = None
        
        self.setup_ui()
        
        # --- AUDIO SETUP ---
        try:
            self.snd_win = pygame.mixer.Sound("win.mp3")
            self.snd_lose = pygame.mixer.Sound("lose.mp3")
            self.snd_life = pygame.mixer.Sound("life.mp3")
        except:
            self.snd_win = None
            self.snd_lose = None
            self.snd_life = None
            
        self.game_over_played = False
        self.player_was_alive = True
        self.play_music("background.mp3")

    def play_music(self, filename):
        """Fungsi pembantu untuk memutar BGM agar tidak error jika file tidak ada"""
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(-1) # Play loop
        except:
            print(f"BGM '{filename}' belum ada di folder.")

    def setup_ui(self):
        cx = WIDTH // 2
        self.btn_start = Button(cx - 150, 350, 300, 60, "START MATCH")
        self.btn_char_index = Button(cx - 150, 430, 300, 60, "CHARACTER INDEX")
        self.btn_quit = Button(cx - 150, 510, 300, 60, "QUIT", bg_color=(150, 50, 50))
        
        self.btn_map = Button(cx - 150, 70, 300, 50, self.maps[self.sel_map_idx], bg_color=(60, 60, 80))
        self.btn_mc_class = Button(cx - 150, 140, 300, 50, f"My Class: {self.mc_classes[self.sel_mc_idx]}", bg_color=(80, 40, 40))
        self.spin_target = NumberSpinner(cx - 110, 210, "Win Score:", start_val=3)
        self.btn_battle = Button(cx - 125, 620, 250, 70, "BATTLE!", font_size=45, bg_color=(180, 140, 20))
        self.btn_back = Button(20, 20, 120, 40, "Back")
        
        start_y = 280
        self.my_spinners = [NumberSpinner(150, start_y + (i*50), c) for i, c in enumerate(self.mc_classes)]
        self.enemy_spinners = [NumberSpinner(850, start_y + (i*50), c) for i, c in enumerate(self.mc_classes)]
        
        self.btn_random_enemy = Button(850, 540, 220, 40, "Randomize Bots", font_size=25)
        self.btn_pause_game = Button(WIDTH - 70, 20, 50, 50, "||", font_size=30, bg_color=(150, 50, 50))
        self.btn_resume = Button(cx - 150, 300, 300, 60, "CONTINUE")
        self.btn_restart = Button(cx - 150, 380, 300, 60, "RESTART")
        self.btn_menu = Button(cx - 150, 460, 300, 60, "MAIN MENU", bg_color=(150, 50, 50))

    def start_match(self):
        self.all_sprites = pygame.sprite.Group()
        self.bots = []
        
        # Pilihan Map
        if self.sel_map_idx == 0:
            self.current_map = MapForest()
        elif self.sel_map_idx == 1:
            self.current_map = MapDesert()
        else:
            self.current_map = MapIce()
            
        map_w = getattr(self.current_map, 'map_width', WIDTH)
        map_h = getattr(self.current_map, 'map_height', HEIGHT)
        self.world_sprites = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        
        spawn_x_blue, spawn_x_red = 300, map_w - 300
        spawn_y = map_h // 2

        self.blue_flag = Flag(spawn_x_blue, spawn_y, "BLUE")
        self.red_flag = Flag(spawn_x_red, spawn_y, "RED")
        self.all_sprites.add(self.blue_flag, self.red_flag)
        
        self.combat_manager = CombatManager()
        self.match_manager = MatchManager(self.spin_target.value)
        self.spawn_manager = SpawnManager((spawn_x_blue, spawn_y), (spawn_x_red, spawn_y))
        self.flag_manager = FlagManager(self.blue_flag, self.red_flag, (spawn_x_blue, spawn_y), (spawn_x_red, spawn_y), self.match_manager)
        self.ai_controller = AIController((spawn_x_blue, spawn_y), (spawn_x_red, spawn_y), self.combat_manager)

        classes_dict = {"Assassin": Assassin, "Knight": Knight, "Tank": Tank, "Wizard": Wizard, "Support": Support}
        selected_class = classes_dict[self.mc_classes[self.sel_mc_idx]]
        self.player = selected_class(spawn_x_blue, spawn_y, "PLAYER")
        self.player.is_mc = True
        self.all_sprites.add(self.player)

        classes_ref = [Assassin, Knight, Tank, Wizard, Support]
        for i, spinner in enumerate(self.my_spinners):
            for _ in range(spinner.value):
                bot = classes_ref[i](spawn_x_blue + random.randint(-100, 100), spawn_y + random.randint(-100, 100), "PLAYER")
                self.all_sprites.add(bot); self.bots.append(bot)
        for i, spinner in enumerate(self.enemy_spinners):
            for _ in range(spinner.value):
                bot = classes_ref[i](spawn_x_red + random.randint(-100, 100), spawn_y + random.randint(-100, 100), "ENEMY")
                self.all_sprites.add(bot); self.bots.append(bot)

        # --- AUDIO SAAT BATTLE ---
        self.state = "PLAYING"
        self.play_music("battle.mp3")
        self.game_over_played = False
        self.player_was_alive = True

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.state == "MENU":
            self.btn_start.check_hover(mouse_pos); self.btn_char_index.check_hover(mouse_pos); self.btn_quit.check_hover(mouse_pos)
        elif self.state == "LOBBY":
            self.btn_map.check_hover(mouse_pos); self.btn_mc_class.check_hover(mouse_pos); self.btn_battle.check_hover(mouse_pos)
            self.btn_back.check_hover(mouse_pos); self.btn_random_enemy.check_hover(mouse_pos)
        elif self.state == "PLAYING":
            self.btn_pause_game.check_hover(mouse_pos)
        elif self.state in ["PAUSED", "GAME_OVER"]:
            self.btn_restart.check_hover(mouse_pos); self.btn_menu.check_hover(mouse_pos)
            if self.state == "PAUSED": self.btn_resume.check_hover(mouse_pos)
        elif self.state == "CHAR_INDEX":
            self.btn_back.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.state == "CHAR_INDEX":
                self.index_screen.handle_event(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == "PLAYING": self.state = "PAUSED"
                elif self.state == "PAUSED": self.state = "PLAYING"
            
            if self.state == "MENU":
                if self.btn_start.is_clicked(event): self.state = "LOBBY"
                if self.btn_char_index.is_clicked(event): self.state = "CHAR_INDEX"
                if self.btn_quit.is_clicked(event): pygame.quit(); sys.exit()
                    
            elif self.state == "LOBBY":
                if self.btn_back.is_clicked(event): self.state = "MENU"
                if self.btn_battle.is_clicked(event): self.start_match()
                if self.btn_map.is_clicked(event):
                    self.sel_map_idx = (self.sel_map_idx + 1) % len(self.maps)
                    self.btn_map.text = self.maps[self.sel_map_idx]
                if self.btn_mc_class.is_clicked(event):
                    self.sel_mc_idx = (self.sel_mc_idx + 1) % len(self.mc_classes)
                    self.btn_mc_class.text = f"My Class: {self.mc_classes[self.sel_mc_idx]}"
                if self.btn_random_enemy.is_clicked(event):
                    for spin in self.enemy_spinners: spin.value = random.randint(0, 2)
                self.spin_target.handle_event(event, mouse_pos, 10, 1)
                for spin in self.my_spinners + self.enemy_spinners: spin.handle_event(event, mouse_pos)
                    
            elif self.state == "PLAYING":
                if self.btn_pause_game.is_clicked(event): self.state = "PAUSED"
                if event.type == pygame.KEYDOWN and self.player.alive():
                    if event.key == pygame.K_f: self.player.action_melee()
                    elif event.key == pygame.K_g: 
                        p_type = self.player.action_ranged()
                        if p_type:
                            dir_x = 1 if self.player.facing == "RIGHT" else -1
                            target_pos = (self.player.pos.x + dir_x * 500, self.player.pos.y)
                            self.combat_manager.spawn_projectile(self.player, target_pos, p_type)
                    elif event.key == pygame.K_h: self.player.action_defense()
                    elif event.key == pygame.K_j: self.player.action_ultimate()

            elif self.state in ["PAUSED", "GAME_OVER"]:
                if self.state == "PAUSED" and self.btn_resume.is_clicked(event): self.state = "PLAYING"
                if self.btn_restart.is_clicked(event): self.start_match()
                if self.btn_menu.is_clicked(event): 
                    self.state = "MENU"
                    self.play_music("background.mp3") # Kembali ke menu, nyalakan BGM menu
                
            elif self.state == "CHAR_INDEX":
                if self.btn_back.is_clicked(event): self.state = "MENU"

    def update(self):
        if self.state == "PLAYING":
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if self.player.alive():
                if keys[pygame.K_w]: dy = -1
                if keys[pygame.K_s]: dy = 1
                if keys[pygame.K_a]: dx = -1
                if keys[pygame.K_d]: dx = 1
            
            map_w = getattr(self.current_map, 'map_width', WIDTH)
            map_h = getattr(self.current_map, 'map_height', HEIGHT)
            
            if (dx != 0 or dy != 0) and self.player.alive():
                self.player.move(dx, dy)
                self.player.rect.clamp_ip(pygame.Rect(0, 0, map_w, map_h))
                self.player.pos.x, self.player.pos.y = self.player.rect.centerx, self.player.rect.centery
                
            alive_chars = [s for s in self.all_sprites if hasattr(s, 'hp')]
            self.combat_manager.update(alive_chars, self.spawn_manager)
            
            player_ref = [self.player]
            self.spawn_manager.update(self.all_sprites, self.bots, player_ref)
            self.player = player_ref[0]

            self.ai_controller.update(self.bots, alive_chars, self.blue_flag, self.red_flag)
            self.flag_manager.update(alive_chars)
            self.all_sprites.update()
            
            if self.player.alive():
                self.camera_x = max(0, min(self.player.rect.centerx - WIDTH // 2, map_w - WIDTH))
                self.camera_y = max(0, min(self.player.rect.centery - HEIGHT // 2, map_h - HEIGHT))
            
            # --- AUDIO RESPAWN (LFE.MP3) ---
            player_is_alive = self.player.alive()
            if not self.player_was_alive and player_is_alive:
                if self.snd_life: self.snd_life.play()
            self.player_was_alive = player_is_alive

            # --- AUDIO GAME OVER (WIN/LOSE) ---
            if self.match_manager.winner: 
                self.state = "GAME_OVER"
                if not self.game_over_played:
                    pygame.mixer.music.stop() # Matikan BGM Battle
                    if self.match_manager.winner == "BLUE TEAM": # Asumsi BLUE adalah player
                        if self.snd_win: self.snd_win.play()
                    else:
                        if self.snd_lose: self.snd_lose.play()
                    self.game_over_played = True

    def draw_text_shadow(self, text, font, color, x, y):
        shadow = font.render(text, True, BLACK)
        surf = font.render(text, True, color)
        self.screen.blit(shadow, (x+3, y+3)); self.screen.blit(surf, (x, y))

    def draw(self):
        if self.state == "MENU":
            self.screen.fill((25, 30, 45)) 
            self.draw_text_shadow("FLAGFALL ARENA", self.font_title, (240, 190, 50), WIDTH//2 - 320, 120)
            self.btn_start.draw(self.screen); self.btn_char_index.draw(self.screen); self.btn_quit.draw(self.screen)
        elif self.state == "LOBBY":
            self.screen.fill((35, 45, 60))
            self.btn_back.draw(self.screen); self.btn_map.draw(self.screen); self.btn_mc_class.draw(self.screen) 
            self.spin_target.draw(self.screen); self.btn_battle.draw(self.screen)
            self.draw_text_shadow("YOUR BOTS", self.font_subtitle, (100, 200, 255), 150, 230)
            for spin in self.my_spinners: spin.draw(self.screen)
            self.draw_text_shadow("ENEMY BOTS", self.font_subtitle, (255, 100, 100), 850, 230)
            for spin in self.enemy_spinners: spin.draw(self.screen)
            self.btn_random_enemy.draw(self.screen)
            pygame.draw.line(self.screen, (100, 100, 120), (WIDTH//2, 230), (WIDTH//2, 550), 2)
        elif self.state == "CHAR_INDEX":
            self.index_screen.draw(self.screen); self.btn_back.draw(self.screen) 
        elif self.state in ["PLAYING", "PAUSED", "GAME_OVER"]:
            try: self.current_map.draw(self.screen, self.camera_x, self.camera_y)
            except TypeError: self.current_map.draw(self.screen)
            self.world_sprites.fill((0, 0, 0, 0)) 
            self.all_sprites.draw(self.world_sprites)
            self.combat_manager.draw(self.world_sprites)
            for sprite in self.all_sprites:
                if hasattr(sprite, 'draw_extras'): sprite.draw_extras(self.world_sprites)
                if hasattr(sprite, 'hp'):
                    hp_r = max(0, sprite.hp / sprite.max_hp)
                    pygame.draw.rect(self.world_sprites, (255, 0, 0), (sprite.rect.left, sprite.rect.top - 15, sprite.rect.width, 5))
                    pygame.draw.rect(self.world_sprites, (0, 255, 0), (sprite.rect.left, sprite.rect.top - 15, int(sprite.rect.width * hp_r), 5))
            self.screen.blit(self.world_sprites, (-self.camera_x, -self.camera_y))
            score_txt = f"{self.match_manager.blue_score} - {self.match_manager.red_score}"
            self.draw_text_shadow(score_txt, self.font_score, WHITE, WIDTH//2 - 60, 20)
            if self.state == "PLAYING": self.btn_pause_game.draw(self.screen)
            if self.state in ["PAUSED", "GAME_OVER"]:
                overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(180); overlay.fill(BLACK); self.screen.blit(overlay, (0, 0))
                title = "PAUSED" if self.state == "PAUSED" else f"{self.match_manager.winner} WINS!"
                self.draw_text_shadow(title, self.font_title, WHITE, WIDTH//2 - 200, 100)
                if self.state == "PAUSED": self.btn_resume.draw(self.screen)
                self.btn_restart.draw(self.screen); self.btn_menu.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events(); self.update(); self.draw(); self.clock.tick(FPS)

if __name__ == "__main__":
    game = FlagfallArena(); game.run()