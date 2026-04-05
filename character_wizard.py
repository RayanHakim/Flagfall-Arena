import pygame
import math
import random
from character_base import Character
from setting import *

class Wizard(Character):
    def __init__(self, x, y, team):
        super().__init__(x, y, team)
        
        self.max_hp = 80
        self.hp = self.max_hp
        self.attack_power = 20
        
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        self.base_max_speed = 4.0
        self.max_speed = self.base_max_speed
        self.acceleration = 0.5  
        self.friction = -0.12    
        
        self.state = "IDLE" 
        self.facing = "RIGHT"
        
        self.anim_timer = 0
        self.anim_speed = 0.09 
        
        self.width = 90
        self.height = 90
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        self.is_attacking = False
        self.attack_duration = 300 
        self.attack_start_time = 0
        
        self.is_casting = False
        self.cast_duration = 400
        self.cast_start_time = 0
        self.last_fire_time = -2000
        self.fire_cooldown = 800 # Cooldown tembakan bola api
        
        self.blink_cooldown = 3000
        self.last_blink_time = -3000
        
        self.is_ulting = False
        self.ult_duration = 800
        self.ult_start_time = 0
        self.ult_cooldown = 7000
        self.last_ult_time = -7000
        
        self.magic_particles = [] 
        self.meteor_particles = []
        
        self.c_robe = (100, 30, 140)     
        self.c_robe_dark = (70, 20, 100) 
        self.c_trim = (255, 215, 0)      
        self.c_skin = (255, 220, 180)    
        self.c_fire = (255, 100, 0)      
        self.c_magic = (200, 50, 255)    
        self.c_team = BLUE if team == "PLAYER" else RED

    def move(self, dx, dy):
        if self.state in ["ATTACK", "CAST", "ULT"]:
            return 
            
        self.acc.x = dx * self.acceleration
        self.acc.y = dy * self.acceleration
        
        if dx > 0: self.facing = "RIGHT"
        elif dx < 0: self.facing = "LEFT"
        
        if dx != 0 or dy != 0:
            self.state = "RUN"
        else:
            self.state = "IDLE"

    def apply_physics(self):
        self.acc.x += self.vel.x * self.friction
        self.acc.y += self.vel.y * self.friction
        self.vel += self.acc
        
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
            
        if self.vel.length() < 0.5 and self.acc.length() < 0.1:
            self.vel.x = 0
            self.vel.y = 0
            if not self.is_attacking and not self.is_casting and not self.is_ulting:
                self.state = "IDLE"
                
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.acc = pygame.math.Vector2(0, 0)

    def action_melee(self):
        current_time = pygame.time.get_ticks()
        if not self.is_attacking and not self.is_casting and not self.is_ulting:
            self.state = "ATTACK"
            self.is_attacking = True
            self.attack_start_time = current_time

    def action_ranged(self):
        """Skill G: Melempar Bola Api"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time >= self.fire_cooldown:
            if not self.is_attacking and not self.is_casting and not self.is_ulting:
                self.state = "CAST"
                self.is_casting = True
                self.cast_start_time = current_time
                self.last_fire_time = current_time
                return "fire" # Mengirim tipe proyektil agar dilempar oleh main.py
        return None

    def action_defense(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_blink_time >= self.blink_cooldown:
            if not self.is_attacking and not self.is_casting and not self.is_ulting:
                for _ in range(15):
                    self.magic_particles.append({
                        'pos': [self.pos.x + random.randint(-20, 20), self.pos.y + random.randint(-20, 30)],
                        'vel': [random.uniform(-2, 2), random.uniform(-2, 2)],
                        'timer': 255,
                        'color': self.c_magic
                    })
                
                blink_dist = 120
                dir_x = 1 if self.facing == "RIGHT" else -1
                self.pos.x += blink_dist * dir_x
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                self.last_blink_time = current_time
                
                for _ in range(15):
                    self.magic_particles.append({
                        'pos': [self.pos.x + random.randint(-20, 20), self.pos.y + random.randint(-20, 30)],
                        'vel': [random.uniform(-1, 1), random.uniform(-3, 0)],
                        'timer': 255,
                        'color': WHITE
                    })

    def action_ultimate(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_ult_time >= self.ult_cooldown:
            if not self.is_ulting:
                self.state = "ULT"
                self.is_ulting = True
                self.ult_start_time = current_time
                self.last_ult_time = current_time
                self.vel.x = 0
                self.vel.y = 0
                
                target_x = self.pos.x + (150 if self.facing == "RIGHT" else -150)
                target_y = self.pos.y + 20
                
                self.meteor_particles.append({
                    'start': [target_x + 100, target_y - 400],
                    'current': [target_x + 100, target_y - 400],
                    'target': [target_x, target_y],
                    'progress': 0.0,
                    'exploded': False,
                    'radius': 20
                })

    def update_states(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_attacking:
            if current_time - self.attack_start_time >= self.attack_duration:
                self.is_attacking = False
                self.state = "IDLE"
                
        if self.is_casting:
            if current_time - self.cast_start_time >= self.cast_duration:
                self.is_casting = False
                self.state = "IDLE"
                
        if self.is_ulting:
            if current_time - self.ult_start_time >= self.ult_duration:
                self.is_ulting = False
                self.state = "IDLE"

    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        self.anim_timer += self.anim_speed
        
        hover_y = math.sin(self.anim_timer) * 3
        bob_x = math.cos(self.anim_timer) * 2 if self.state == "RUN" else 0
        
        base_y = 45 + hover_y
        base_x = 45 + bob_x
        dir_x = 1 if self.facing == "RIGHT" else -1

        robe_base = [
            (base_x - 12, base_y - 10), (base_x + 12, base_y - 10),
            (base_x + 18, base_y + 30), (base_x - (5*dir_x), base_y + 35),
            (base_x - 20, base_y + 30)
        ]
        pygame.draw.polygon(self.image, self.c_robe_dark, robe_base)
        
        robe_outer = [
            (base_x - 14, base_y - 15), (base_x + 12, base_y - 15),
            (base_x + (15*dir_x), base_y + 25), (base_x, base_y + 32),
            (base_x - (22*dir_x), base_y + 25)
        ]
        pygame.draw.polygon(self.image, self.c_robe, robe_outer)
        pygame.draw.polygon(self.image, self.c_trim, robe_outer, 2) 

        pygame.draw.ellipse(self.image, self.c_robe, (base_x - 14, base_y - 20, 28, 30))
        
        head_x = base_x + (2 * dir_x)
        head_y = base_y - 25
        pygame.draw.circle(self.image, self.c_skin, (int(head_x), int(head_y)), 9)
        
        hat_pts = [
            (head_x - 15, head_y - 4), (head_x + 15, head_y - 4), 
            (head_x + (18*dir_x), head_y), (head_x - (18*dir_x), head_y)
        ]
        pygame.draw.polygon(self.image, self.c_robe_dark, hat_pts)
        
        hat_cone = [
            (head_x - 12, head_y - 4), (head_x + 12, head_y - 4),
            (head_x - (15*dir_x) - bob_x, head_y - 35) 
        ]
        pygame.draw.polygon(self.image, self.c_robe, hat_cone)
        pygame.draw.polygon(self.image, self.c_trim, hat_cone, 2)

        arm_color = self.c_robe_dark
        if self.state == "ATTACK":
            progress = (pygame.time.get_ticks() - self.attack_start_time) / self.attack_duration
            hand_x = base_x + (25 * dir_x)
            hand_y = base_y + math.sin(progress * math.pi) * 10
            pygame.draw.line(self.image, arm_color, (base_x, base_y - 10), (hand_x, hand_y), 6)
            pygame.draw.circle(self.image, self.c_skin, (int(hand_x), int(head_y + 15)), 4)
            
        elif self.state == "CAST":
            # Animasi saat merapal: Tangan kedepan dan ada bola api kecil sebentar
            hand_x = base_x + (25 * dir_x)
            hand_y = base_y - 5
            pygame.draw.line(self.image, arm_color, (base_x, base_y - 10), (hand_x, hand_y), 6)
            pygame.draw.circle(self.image, self.c_skin, (int(hand_x), int(hand_y)), 4)
            
            # Bola api di tangan
            glow_radius = 6 + int(math.sin(self.anim_timer * 15) * 3)
            pygame.draw.circle(self.image, self.c_fire, (int(hand_x + (5*dir_x)), int(hand_y)), glow_radius)
            pygame.draw.circle(self.image, (255, 255, 0), (int(hand_x + (5*dir_x)), int(hand_y)), glow_radius - 3)
            
        elif self.state == "ULT":
            hand_x = base_x + (5 * dir_x)
            hand_y = base_y - 30
            pygame.draw.line(self.image, arm_color, (base_x, base_y - 10), (hand_x, hand_y), 6)
            pygame.draw.circle(self.image, self.c_skin, (int(hand_x), int(hand_y)), 4)
            pygame.draw.circle(self.image, self.c_magic, (int(hand_x), int(hand_y - 5)), 15, 2)
            
        else:
            hand_x = base_x + (10 * dir_x)
            hand_y = base_y + 5
            pygame.draw.line(self.image, arm_color, (base_x, base_y - 10), (hand_x, hand_y), 6)
            pygame.draw.circle(self.image, self.c_skin, (int(hand_x), int(hand_y)), 4)

        pygame.draw.ellipse(self.image, (0, 0, 0, 50), (base_x - 15, 75, 30, 8))
        pygame.draw.ellipse(self.image, self.c_team, (base_x - 15, 75, 30, 8), 2)

    def update_particles(self, screen):
        for p in self.magic_particles[:]:
            p['timer'] -= 10
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            
            if p['timer'] <= 0:
                self.magic_particles.remove(p)
            else:
                alpha = max(0, p['timer'])
                surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*p['color'][:3], alpha), (3, 3), 3)
                screen.blit(surf, (int(p['pos'][0]), int(p['pos'][1])))

        for m in self.meteor_particles[:]:
            if not m['exploded']:
                m['progress'] += 0.05
                m['current'][0] = m['start'][0] + (m['target'][0] - m['start'][0]) * m['progress']
                m['current'][1] = m['start'][1] + (m['target'][1] - m['start'][1]) * m['progress']
                
                for _ in range(3):
                    self.magic_particles.append({
                        'pos': [m['current'][0] + random.randint(-10, 10), m['current'][1] + random.randint(-10, 10)],
                        'vel': [random.uniform(-1, 1), random.uniform(-1, 1)],
                        'timer': 200,
                        'color': self.c_fire
                    })
                
                pygame.draw.circle(screen, self.c_fire, (int(m['current'][0]), int(m['current'][1])), m['radius'])
                pygame.draw.circle(screen, (255, 255, 0), (int(m['current'][0]), int(m['current'][1])), m['radius'] - 5)
                
                if m['progress'] >= 1.0:
                    m['exploded'] = True
                    m['timer'] = 255
            else:
                m['timer'] -= 15
                if m['timer'] <= 0:
                    self.meteor_particles.remove(m)
                else:
                    alpha = max(0, m['timer'])
                    exp_radius = 60 + (255 - m['timer']) / 2
                    surf = pygame.Surface((exp_radius*2, exp_radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (255, 100, 0, alpha), (exp_radius, exp_radius), exp_radius)
                    pygame.draw.circle(surf, (255, 200, 0, alpha), (exp_radius, exp_radius), exp_radius*0.7)
                    screen.blit(surf, (int(m['target'][0] - exp_radius), int(m['target'][1] - exp_radius)))

    def update(self):
        self.update_states()
        self.apply_physics()
        self.draw_shape()

    def draw_extras(self, screen):
        self.update_particles(screen)
        
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_ult_time < self.ult_cooldown:
            cd_ratio = (current_time - self.last_ult_time) / self.ult_cooldown
            pygame.draw.rect(screen, (50, 50, 50), (self.rect.centerx - 20, self.rect.top - 15, 40, 4))
            pygame.draw.rect(screen, self.c_fire, (self.rect.centerx - 20, self.rect.top - 15, int(40 * cd_ratio), 4))
            
        elif current_time - self.last_blink_time < self.blink_cooldown:
            cd_ratio = (current_time - self.last_blink_time) / self.blink_cooldown
            pygame.draw.rect(screen, (50, 50, 50), (self.rect.centerx - 20, self.rect.top - 15, 40, 4))
            pygame.draw.rect(screen, self.c_magic, (self.rect.centerx - 20, self.rect.top - 15, int(40 * cd_ratio), 4))