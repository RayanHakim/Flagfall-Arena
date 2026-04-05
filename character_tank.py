import pygame
import math
import random
from character_base import Character
from setting import *

class Tank(Character):
    def __init__(self, x, y, team):
        super().__init__(x, y, team)
        
        self.max_hp = 300
        self.hp = self.max_hp
        self.attack_power = 10
        
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        self.base_max_speed = 2.5 
        self.max_speed = self.base_max_speed
        self.acceleration = 0.4  
        self.friction = -0.25    
        
        self.state = "IDLE"
        self.facing = "RIGHT"
        
        self.anim_timer = 0
        self.anim_speed = 0.05 
        
        self.width = 110
        self.height = 110
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        self.is_attacking = False
        self.attack_duration = 600 
        self.attack_start_time = 0
        
        self.is_fortified = False
        
        # Skill G: Rock Throw
        self.is_throwing = False
        self.throw_duration = 400
        self.last_throw_time = -4000
        self.throw_cooldown = 4000

        self.is_shattering = False
        self.shatter_duration = 500
        self.shatter_start_time = 0
        self.shatter_cooldown = 6000 
        self.last_shatter_time = -6000
        
        self.shockwaves = [] 
        
        self.c_armor = (90, 70, 50)      
        self.c_armor_dark = (60, 40, 30) 
        self.c_metal = (120, 120, 120)   
        self.c_core = (255, 100, 0)      
        self.c_team = BLUE if team == "PLAYER" else RED

    def move(self, dx, dy):
        if self.state in ["ATTACK", "SHATTER", "THROW"]:
            return 
            
        self.acc.x = dx * self.acceleration
        self.acc.y = dy * self.acceleration
        
        if dx > 0: self.facing = "RIGHT"
        elif dx < 0: self.facing = "LEFT"
        
        if dx != 0 or dy != 0:
            if not self.is_fortified:
                self.state = "RUN"
        else:
            if not self.is_fortified:
                self.state = "IDLE"

    def apply_physics(self):
        if self.state == "SHATTER" or self.state == "THROW":
            self.vel.x = 0 
            self.vel.y = 0
        else:
            self.acc.x += self.vel.x * self.friction
            self.acc.y += self.vel.y * self.friction
            self.vel += self.acc
            
            if self.vel.length() > self.max_speed:
                self.vel.scale_to_length(self.max_speed)
                
            if self.vel.length() < 0.2 and self.acc.length() < 0.1:
                self.vel.x = 0
                self.vel.y = 0
                if not self.is_fortified and not self.is_shattering and not self.is_throwing:
                    self.state = "IDLE"
                
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.acc = pygame.math.Vector2(0, 0)

    def action_melee(self):
        current_time = pygame.time.get_ticks()
        if not self.is_attacking and not self.is_shattering and not self.is_fortified and not self.is_throwing:
            self.state = "ATTACK"
            self.is_attacking = True
            self.attack_start_time = current_time

    def action_ranged(self):
        """Skill G: Melempar Batu Besar (Rock Throw)"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_throw_time >= self.throw_cooldown:
            if not self.is_attacking and not self.is_shattering:
                self.state = "THROW"
                self.is_throwing = True
                self.is_fortified = False
                self.attack_start_time = current_time # Reusing timer for duration
                self.last_throw_time = current_time
                return "boulder"
        return None

    def action_defense(self):
        if not self.is_attacking and not self.is_shattering and not self.is_throwing:
            self.is_fortified = not self.is_fortified
            if self.is_fortified:
                self.state = "DEFEND"
                self.max_speed = self.base_max_speed * 0.2 
            else:
                self.state = "IDLE"
                self.max_speed = self.base_max_speed

    def action_ultimate(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shatter_time >= self.shatter_cooldown:
            if not self.is_shattering and not self.is_throwing:
                self.state = "SHATTER"
                self.is_shattering = True
                self.is_fortified = False
                self.max_speed = self.base_max_speed
                self.shatter_start_time = current_time
                self.last_shatter_time = current_time
                
                self.shockwaves.append({
                    'pos': [self.pos.x, self.pos.y + 30],
                    'radius': 10,
                    'max_radius': 150,
                    'alpha': 255
                })

    def update_states(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_attacking:
            if current_time - self.attack_start_time >= self.attack_duration:
                self.is_attacking = False
                self.state = "IDLE"

        if self.is_throwing:
            if current_time - self.attack_start_time >= self.throw_duration:
                self.is_throwing = False
                self.state = "IDLE"
                
        if self.is_shattering:
            if current_time - self.shatter_start_time >= self.shatter_duration:
                self.is_shattering = False
                self.state = "IDLE"

    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        self.anim_timer += self.anim_speed
        
        breathe = math.sin(self.anim_timer) * 2 if self.state == "IDLE" else 0
        run_bob = abs(math.sin(self.anim_timer * 2)) * 4 if self.state == "RUN" else 0
        
        base_y = 55 + breathe - run_bob
        base_x = 55
        dir_x = 1 if self.facing == "RIGHT" else -1

        if self.is_fortified:
            base_y += 5
            pygame.draw.rect(self.image, (255, 150, 0, 100), (base_x - 35, base_y - 45, 70, 90), border_radius=10)
            pygame.draw.rect(self.image, (255, 200, 50, 200), (base_x - 35, base_y - 45, 70, 90), 4, border_radius=10)

        # Kaki
        if self.state == "RUN":
            leg1_y = math.cos(self.anim_timer * 2) * 6
            leg2_y = math.cos(self.anim_timer * 2 + math.pi) * 6
            pygame.draw.rect(self.image, self.c_armor_dark, (base_x - 18, base_y + 15, 16, 25 + leg1_y), border_radius=4)
            pygame.draw.rect(self.image, self.c_armor_dark, (base_x + 2, base_y + 15, 16, 25 + leg2_y), border_radius=4)
        else:
            pygame.draw.rect(self.image, self.c_armor_dark, (base_x - 20, base_y + 15, 18, 25), border_radius=4)
            pygame.draw.rect(self.image, self.c_armor_dark, (base_x + 2, base_y + 15, 18, 25), border_radius=4)

        # Tubuh
        torso_rect = pygame.Rect(0, 0, 50, 45)
        torso_rect.center = (base_x, base_y - 5)
        pygame.draw.rect(self.image, self.c_armor, torso_rect, border_radius=8)
        pygame.draw.circle(self.image, self.c_core, (base_x, base_y - 5), 8)
        pygame.draw.circle(self.image, (255, 200, 100), (base_x, base_y - 5), 4)

        # Pundak
        pygame.draw.rect(self.image, self.c_armor_dark, (base_x - 35, base_y - 25, 20, 25), border_radius=6)
        pygame.draw.rect(self.image, self.c_armor_dark, (base_x + 15, base_y - 25, 20, 25), border_radius=6)

        # Kepala
        head_x = base_x + (5 * dir_x)
        head_y = base_y - 35
        pygame.draw.rect(self.image, self.c_armor, (head_x - 12, head_y - 12, 24, 24), border_radius=4)
        eye_x = head_x + (6 * dir_x)
        pygame.draw.line(self.image, self.c_core, (eye_x - 4, head_y), (eye_x + 4, head_y), 4)

        # Senjata (Palu) & Pose Melempar
        if self.state == "THROW":
            # Pose melempar batu (mengangkat tangan)
            pygame.draw.circle(self.image, (100, 100, 100), (base_x + 20*dir_x, base_y - 20), 15) # Visual batu yang dipegang
            pygame.draw.line(self.image, self.c_metal, (base_x, base_y), (base_x + 5*dir_x, base_y + 30), 8) # Palu ditaruh di bawah
        elif self.state == "ATTACK" or self.state == "SHATTER":
            progress = (pygame.time.get_ticks() - self.attack_start_time) / self.attack_duration
            if self.state == "SHATTER":
                progress = (pygame.time.get_ticks() - self.shatter_start_time) / self.shatter_duration
            angle = -math.pi/2 + (progress * math.pi)
            if self.facing == "LEFT": angle = math.pi - angle
            handle_len = 40
            hammer_end_x = base_x + math.cos(angle) * handle_len
            hammer_end_y = base_y + math.sin(angle) * handle_len
            pygame.draw.line(self.image, self.c_metal, (base_x, base_y), (hammer_end_x, hammer_end_y), 8)
            hammer_head = pygame.Rect(0, 0, 25, 45)
            hammer_head.center = (hammer_end_x, hammer_end_y)
            pygame.draw.rect(self.image, self.c_armor_dark, hammer_head, border_radius=4)
            pygame.draw.rect(self.image, self.c_core, hammer_head, 3, border_radius=4)
        else:
            handle_top_x = base_x + (15 * dir_x)
            handle_top_y = base_y - 35
            handle_bot_x = base_x + (5 * dir_x)
            handle_bot_y = base_y + 25
            pygame.draw.line(self.image, self.c_metal, (handle_bot_x, handle_bot_y), (handle_top_x, handle_top_y), 8)
            hammer_head = pygame.Rect(0, 0, 25, 45)
            hammer_head.center = (handle_top_x, handle_top_y)
            pygame.draw.rect(self.image, self.c_armor_dark, hammer_head, border_radius=4)
            pygame.draw.rect(self.image, self.c_core, hammer_head, 3, border_radius=4)

        pygame.draw.ellipse(self.image, (0, 0, 0, 80), (base_x - 30, base_y + 35, 60, 15))
        pygame.draw.ellipse(self.image, self.c_team, (base_x - 30, base_y + 35, 60, 15), 3)

    def update_particles(self, screen):
        for wave in self.shockwaves[:]:
            wave['radius'] += 8 
            wave['alpha'] -= 10
            if wave['alpha'] <= 0 or wave['radius'] >= wave['max_radius']:
                self.shockwaves.remove(wave)
            else:
                alpha = max(0, wave['alpha'])
                wave_surf = pygame.Surface((wave['max_radius']*2, wave['max_radius']*2), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, (255, 100, 0, alpha), (wave['max_radius'], wave['max_radius']), int(wave['radius']), 6)
                pygame.draw.circle(wave_surf, (200, 50, 0, alpha//2), (wave['max_radius'], wave['max_radius']), int(wave['radius'] - 10), 4)
                screen.blit(wave_surf, (int(wave['pos'][0] - wave['max_radius']), int(wave['pos'][1] - wave['max_radius'])))

    def update(self):
        self.update_states()
        self.apply_physics()
        self.draw_shape()

    def draw_extras(self, screen):
        self.update_particles(screen)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shatter_time < self.shatter_cooldown:
            cd_ratio = (current_time - self.last_shatter_time) / self.shatter_cooldown
            pygame.draw.rect(screen, (50, 50, 50), (self.rect.centerx - 30, self.rect.top - 15, 60, 6))
            pygame.draw.rect(screen, self.c_core, (self.rect.centerx - 30, self.rect.top - 15, int(60 * cd_ratio), 6))