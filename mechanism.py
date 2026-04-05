import pygame
import math
import random

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, team, p_type, caster=None):
        super().__init__()
        self.caster = caster  
        self.team = team
        self.p_type = p_type
        self.speed = 12
        self.damage = 15
        self.returning = False 
        
        # Inisialisasi Posisi dengan Vector2
        self.pos = pygame.math.Vector2(x, y)
        
        # Hitung arah awal menggunakan Vector2
        target = pygame.math.Vector2(target_x, target_y)
        direction = target - self.pos
        
        # Penyesuaian Status Berdasarkan Tipe
        if p_type == "boulder":
            self.speed = 9
            self.damage = 35
        elif p_type == "fire": # Cahaya Suci Wizard
            self.speed = 14
            self.damage = 25
        elif p_type == "knight_shield":
            self.speed = 15
            self.damage = 20
        elif p_type == "healing_orb": 
            self.speed = 10
            self.damage = -15 # Negatif = Heal

        if direction.length() > 0:
            self.vel = direction.normalize() * self.speed
        else:
            self.vel = pygame.math.Vector2(self.speed, 0)
        
        # Ukuran kanvas seragam agar tidak terpotong saat diputar
        self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.render_projectile()
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.spawn_time = pygame.time.get_ticks()
        self.rotation = 0

    def render_projectile(self):
        """Menggambar visual proyektil secara prosedural"""
        C_WHITE = (255, 255, 255)
        C_GOLD = (218, 165, 32)
        C_SILVER = (150, 155, 160)
        
        if self.p_type == "knight_shield":
            shield_pts = [(15, 5), (35, 5), (35, 25), (25, 40), (15, 25)]
            pygame.draw.polygon(self.original_image, (90, 95, 100), shield_pts)
            pygame.draw.polygon(self.original_image, C_GOLD, shield_pts, 3)
            pygame.draw.line(self.original_image, (200, 40, 40), (25, 10), (25, 30), 3)

        elif self.p_type == "boulder":
            rock_pts = [(10, 15), (30, 5), (45, 20), (35, 45), (10, 40), (5, 25)]
            pygame.draw.polygon(self.original_image, (100, 100, 100), rock_pts)
            pygame.draw.polygon(self.original_image, (60, 60, 60), rock_pts, 3)
            pygame.draw.line(self.original_image, (80, 80, 80), (15, 15), (30, 30), 2)

        elif self.p_type == "dagger":
            pygame.draw.polygon(self.original_image, (180, 180, 180), [(10, 25), (30, 20), (40, 25), (30, 30)])
            pygame.draw.rect(self.original_image, (70, 70, 70), (5, 23, 8, 4))

        elif self.p_type == "fire": 
            pygame.draw.circle(self.original_image, (255, 255, 150, 150), (25, 25), 15)
            pygame.draw.circle(self.original_image, (255, 255, 0), (25, 25), 10)
            pygame.draw.circle(self.original_image, C_WHITE, (25, 25), 5)

        elif self.p_type == "healing_orb": 
            pygame.draw.circle(self.original_image, (0, 255, 150, 150), (25, 25), 12)
            pygame.draw.circle(self.original_image, (0, 255, 100), (25, 25), 8, 2)

        else:
            pygame.draw.circle(self.original_image, (180, 50, 255), (25, 25), 10)
            pygame.draw.circle(self.original_image, C_WHITE, (25, 25), 4)

    def update(self):
        now = pygame.time.get_ticks()
        
        if self.p_type == "knight_shield":
            self.rotation += 25
            if not self.returning:
                if now - self.spawn_time > 600:
                    self.returning = True
            
            if self.returning and self.caster:
                target_pos = pygame.math.Vector2(self.caster.rect.centerx, self.caster.rect.centery)
                direction = target_pos - self.pos
                if direction.length() > 20:
                    self.vel = direction.normalize() * (self.speed + 4)
                else:
                    if hasattr(self.caster, 'shield_out'):
                        self.caster.shield_out = False 
                    self.kill()
            
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            self.rect = self.image.get_rect(center=self.rect.center)

        elif self.p_type in ["boulder", "fire", "healing_orb"]:
            self.rotation += 15
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            self.rect = self.image.get_rect(center=self.rect.center)

        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if self.p_type != "knight_shield" and now - self.spawn_time > 1500:
            self.kill()


class SpawnManager:
    def __init__(self, blue_base, red_base):
        self.blue_base = blue_base
        self.red_base = red_base
        self.respawn_queue = []
        # Mengubah delay respawn menjadi 5 detik (5000 ms) sesuai permintaan
        self.respawn_delay = 5000 

    def add_to_queue(self, char_obj):
        char_class = type(char_obj)
        respawn_time = pygame.time.get_ticks() + self.respawn_delay
        self.respawn_queue.append({
            'class': char_class,
            'team': char_obj.team,
            'time': respawn_time,
            'is_player': getattr(char_obj, 'is_mc', False) # Gunakan getattr untuk aman
        })

    def update(self, all_sprites, bots_list, player_ref_holder):
        current_time = pygame.time.get_ticks()
        for item in self.respawn_queue[:]:
            if current_time >= item['time']:
                spawn_pos = self.blue_base if item['team'] == "PLAYER" else self.red_base
                new_char = item['class'](spawn_pos[0], spawn_pos[1], item['team'])
                
                all_sprites.add(new_char)
                if not item['is_player']:
                    bots_list.append(new_char)
                else:
                    new_char.is_mc = True
                    player_ref_holder[0] = new_char
                    
                self.respawn_queue.remove(item)


class CombatManager:
    def __init__(self):
        self.projectiles = pygame.sprite.Group()

    def spawn_projectile(self, caster, target_pos, p_type):
        proj = Projectile(caster.rect.centerx, caster.rect.centery, 
                          target_pos[0], target_pos[1], 
                          caster.team, p_type, caster)
        self.projectiles.add(proj)

    def update(self, characters, spawn_manager):
        self.projectiles.update()
        
        for proj in self.projectiles:
            for char in characters:
                if proj.p_type == "healing_orb":
                    if char.team == proj.caster.team and char != proj.caster and char.rect.colliderect(proj.rect):
                        char.hp = min(char.max_hp, char.hp - proj.damage)
                        proj.kill()
                        break
                elif char.team != proj.team and char.rect.colliderect(proj.rect):
                    dmg = proj.damage
                    if hasattr(char, 'state') and char.state == "DEFEND": dmg *= 0.3
                    char.hp -= dmg
                    if proj.p_type != "knight_shield":
                        proj.kill()
                    break
                    
        for char in characters:
            if hasattr(char, 'state') and char.state == "ATTACK" and hasattr(char, 'attack_start_time'):
                time_in_atk = pygame.time.get_ticks() - char.attack_start_time
                if time_in_atk < 50:
                    dir_x = 1 if char.facing == "RIGHT" else -1
                    hitbox = pygame.Rect(char.rect.centerx + (20 * dir_x) - 20, char.rect.centery - 20, 40, 40)
                    for enemy in characters:
                        if enemy.team != char.team and hitbox.colliderect(enemy.rect):
                            dmg = char.attack_power
                            if enemy.state == "DEFEND": dmg *= 0.3
                            enemy.hp -= dmg

        for char in characters:
            if char.hp <= 0:
                spawn_manager.add_to_queue(char)
                char.kill()

    def draw(self, surface):
        self.projectiles.draw(surface)


class MatchManager:
    def __init__(self, target_score):
        self.blue_score = 0
        self.red_score = 0
        self.target_score = target_score
        self.winner = None

    def add_score(self, team):
        if team == "BLUE": self.blue_score += 1
        elif team == "RED": self.red_score += 1
        if self.blue_score >= self.target_score: self.winner = "BLUE TEAM"
        elif self.red_score >= self.target_score: self.winner = "RED TEAM"


class FlagManager:
    def __init__(self, blue_flag, red_flag, blue_base, red_base, match_manager):
        self.blue_flag, self.red_flag = blue_flag, red_flag
        self.blue_base, self.red_base = blue_base, red_base
        self.match = match_manager

    def update(self, characters):
        for char in characters:
            if char.team == "PLAYER":
                if self.red_flag.carrier is None and char.rect.colliderect(self.red_flag.rect):
                    self.red_flag.carrier = char
                if self.red_flag.carrier == char:
                    dist = math.hypot(char.pos.x - self.blue_base[0], char.pos.y - self.blue_base[1])
                    if dist < 100:
                        self.match.add_score("BLUE")
                        self.red_flag.carrier = None
                        self.red_flag.rect.center = self.red_base
            elif char.team == "ENEMY":
                if self.blue_flag.carrier is None and char.rect.colliderect(self.blue_flag.rect):
                    self.blue_flag.carrier = char
                if self.blue_flag.carrier == char:
                    dist = math.hypot(char.pos.x - self.red_base[0], char.pos.y - self.red_base[1])
                    if dist < 100:
                        self.match.add_score("RED")
                        self.blue_flag.carrier = None
                        self.blue_flag.rect.center = self.blue_base

        for flag in [self.blue_flag, self.red_flag]:
            if flag.carrier is not None:
                if not flag.carrier.alive(): flag.carrier = None
                else:
                    flag.rect.centerx = flag.carrier.rect.centerx
                    flag.rect.centery = flag.carrier.rect.centery - 40


class AIController:
    def __init__(self, blue_base, red_base, combat_manager):
        self.blue_base, self.red_base = blue_base, red_base
        self.combat = combat_manager

    def update(self, bots, characters, blue_flag, red_flag):
        for bot in bots[:]:
            if not bot.alive():
                bots.remove(bot)
                continue
            
            nearest_enemy = None
            min_dist = 9999
            for char in characters:
                if char.team != bot.team and char.alive():
                    dist = math.hypot(char.pos.x - bot.pos.x, char.pos.y - bot.pos.y)
                    if dist < min_dist:
                        min_dist, nearest_enemy = dist, char

            if nearest_enemy and min_dist < 350:
                dx, dy = nearest_enemy.pos.x - bot.pos.x, nearest_enemy.pos.y - bot.pos.y
                if min_dist < 60:
                    bot.move(0, 0); bot.action_melee()
                else:
                    bot.move(dx/min_dist, dy/min_dist)
                    if random.random() < 0.02:
                        p_type = self.get_p_type(bot)
                        if hasattr(bot, 'action_ranged'):
                            bot.action_ranged()
                            self.combat.spawn_projectile(bot, nearest_enemy.rect.center, p_type)
                continue

            target_x, target_y = 0, 0
            if bot.team == "PLAYER":
                target_x, target_y = (self.blue_base if red_flag.carrier == bot else red_flag.rect.center)
            else:
                target_x, target_y = (self.red_base if blue_flag.carrier == bot else blue_flag.rect.center)

            dx, dy = target_x - bot.pos.x, target_y - bot.pos.y
            dist = math.hypot(dx, dy)
            if dist > 15: bot.move(dx / dist, dy / dist)
            else: bot.move(0, 0)

    def get_p_type(self, bot):
        cls_name = bot.__class__.__name__
        if cls_name == "Assassin": return "dagger"
        if cls_name == "Knight": return "knight_shield"
        if cls_name == "Tank": return "boulder"
        if cls_name == "Wizard": return "fire"
        if cls_name == "Support": return "healing_orb"
        return "fire"