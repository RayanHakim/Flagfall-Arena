import pygame
import math
import random
from character_base import Character
from setting import *

class Support(Character):
    def __init__(self, x, y, team):
        super().__init__(x, y, team)
        
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack_power = 8   
        
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        self.base_max_speed = 5.0
        self.max_speed = self.base_max_speed
        self.acceleration = 0.6  
        self.friction = -0.10    
        
        self.state = "IDLE" 
        self.facing = "RIGHT"
        
        self.anim_timer = 0
        self.anim_speed = 0.08 
        
        self.width = 90
        self.height = 90
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        self.is_attacking = False
        self.attack_duration = 300 
        self.attack_start_time = 0

        # Skill G: Ranged Holy Light (Healing Orb)
        self.is_casting = False
        self.cast_duration = 400
        self.cast_start_time = 0
        self.last_ranged_time = -3000
        self.ranged_cooldown = 2000 # Cooldown tembakan cahaya suci
        
        self.is_shielded = False
        self.shield_pulse = 0
        
        self.is_healing = False
        self.heal_duration = 1500 
        self.heal_start_time = 0
        self.heal_cooldown = 8000 
        self.last_heal_time = -8000
        
        self.heal_particles = [] 
        
        self.color_robe = (240, 245, 250)      
        self.color_robe_dark = (200, 210, 220) 
        self.color_accent = (0, 200, 255)      
        self.color_staff = (139, 69, 19)       
        self.color_gem = (50, 255, 150)        
        self.color_team = BLUE if team == "PLAYER" else RED

    def move(self, dx, dy):
        if self.state in ["ATTACK", "HEAL", "CAST"]:
            return 
            
        self.acc.x = dx * self.acceleration
        self.acc.y = dy * self.acceleration
        
        if dx > 0: self.facing = "RIGHT"
        elif dx < 0: self.facing = "LEFT"
        
        if dx != 0 or dy != 0:
            if not self.is_shielded:
                self.state = "RUN"
        else:
            if not self.is_shielded:
                self.state = "IDLE"

    def apply_physics(self):
        if self.state == "HEAL" or self.state == "CAST":
            self.vel.x *= 0.8 
            self.vel.y *= 0.8
        else:
            self.acc.x += self.vel.x * self.friction
            self.acc.y += self.vel.y * self.friction
            self.vel += self.acc
            
            if self.vel.length() > self.max_speed:
                self.vel.scale_to_length(self.max_speed)
                
            if self.vel.length() < 0.5 and self.acc.length() < 0.1:
                self.vel.x = 0
                self.vel.y = 0
                if not self.is_shielded and not self.is_healing and not self.is_casting:
                    self.state = "IDLE"
                
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.acc = pygame.math.Vector2(0, 0)

    def action_melee(self):
        current_time = pygame.time.get_ticks()
        if not self.is_attacking and not self.is_healing:
            self.state = "ATTACK"
            self.is_attacking = True
            self.attack_start_time = current_time

    def action_ranged(self):
        """Skill G: Menembakkan Cahaya Suci Penyembuh"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_ranged_time >= self.ranged_cooldown:
            if not self.is_attacking and not self.is_healing:
                self.state = "CAST"
                self.is_casting = True
                self.cast_start_time = current_time
                self.last_ranged_time = current_time
                return "healing_orb" # Diterima oleh mechanism.py
        return None

    def action_defense(self):
        if not self.is_attacking and not self.is_healing:
            self.is_shielded = not self.is_shielded
            if self.is_shielded:
                self.state = "DEFEND"
                self.max_speed = self.base_max_speed * 0.6 
            else:
                self.state = "IDLE"
                self.max_speed = self.base_max_speed

    def action_ultimate(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_heal_time >= self.heal_cooldown:
            if not self.is_healing:
                self.state = "HEAL"
                self.is_healing = True
                self.is_shielded = False 
                self.heal_start_time = current_time
                self.last_heal_time = current_time

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
                
        if self.is_healing:
            if self.hp < self.max_hp:
                self.hp += 0.4 
                if self.hp > self.max_hp: self.hp = self.max_hp

            if random.random() > 0.4:
                offset_x = random.randint(-40, 40)
                offset_y = random.randint(-10, 20)
                self.heal_particles.append({
                    'pos': [self.pos.x + offset_x, self.pos.y + offset_y],
                    'timer': 255
                })
                
            if current_time - self.heal_start_time >= self.heal_duration:
                self.is_healing = False
                self.state = "IDLE"

    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        self.anim_timer += self.anim_speed
        
        hover_y = math.sin(self.anim_timer) * 6
        bob_x = math.cos(self.anim_timer / 2) * 2 if self.state == "RUN" else 0
        
        base_y = 45 + hover_y
        base_x = 45 + bob_x
        dir_x = 1 if self.facing == "RIGHT" else -1

        if self.is_shielded:
            self.shield_pulse += 0.1
            pulse_radius = 35 + math.sin(self.shield_pulse) * 3
            pygame.draw.circle(self.image, (0, 255, 255, 100), (int(base_x), int(base_y)), int(pulse_radius), 3)
            pygame.draw.circle(self.image, (0, 200, 255, 40), (int(base_x), int(base_y)), int(pulse_radius))

        # Jubah
        robe_pts = [
            (base_x - 12, base_y - 5), (base_x + 12, base_y - 5),
            (base_x + 18, base_y + 25), (base_x - (10*dir_x), base_y + 35),
            (base_x - 22, base_y + 20)
        ]
        pygame.draw.polygon(self.image, self.color_robe_dark, robe_pts)
        
        outer_robe = [
            (base_x - 14, base_y - 15), (base_x + 10, base_y - 15),
            (base_x + (15*dir_x), base_y + 15), (base_x, base_y + 28),
            (base_x - (25*dir_x), base_y + 15)
        ]
        pygame.draw.polygon(self.image, self.color_robe, outer_robe)
        pygame.draw.polygon(self.image, self.color_accent, outer_robe, 2) 

        # Kepala
        head_x, head_y = base_x + (3 * dir_x), base_y - 25
        pygame.draw.circle(self.image, (20, 20, 30), (int(head_x), int(head_y)), 10)
        pygame.draw.circle(self.image, self.color_robe, (int(head_x), int(head_y)), 10, 3)
        pygame.draw.circle(self.image, self.color_accent, (int(head_x + 2*dir_x), int(head_y - 2)), 2)

        # Tongkat (Staff)
        staff_y_offset = math.sin(self.anim_timer * 1.5) * 4 
        
        if self.state == "ATTACK":
            progress = (pygame.time.get_ticks() - self.attack_start_time) / self.attack_duration
            angle = -math.pi/4 + (progress * math.pi/2)
            if self.facing == "LEFT": angle = math.pi - angle
            staff_end_x = base_x + math.cos(angle) * 40
            staff_end_y = base_y + math.sin(angle) * 40
            pygame.draw.line(self.image, self.color_staff, (base_x, base_y), (staff_end_x, staff_end_y), 4)
            pygame.draw.circle(self.image, self.color_gem, (int(staff_end_x), int(staff_end_y)), 6)
            
        elif self.state == "CAST":
            # Pose menembak: Tongkat diarahkan lurus ke depan
            staff_x = base_x + (25 * dir_x)
            pygame.draw.line(self.image, self.color_staff, (base_x, base_y + 10), (staff_x, base_y - 20), 4)
            # Efek cahaya di ujung tongkat
            glow = 10 + int(math.sin(self.anim_timer * 20) * 5)
            pygame.draw.circle(self.image, (150, 255, 200, 150), (int(staff_x), int(base_y - 20)), glow)
            pygame.draw.circle(self.image, WHITE, (int(staff_x), int(base_y - 20)), 5)

        elif self.state == "HEAL":
            pygame.draw.line(self.image, self.color_staff, (base_x + (15*dir_x), base_y + 20), (base_x + (15*dir_x), base_y - 35), 4)
            pygame.draw.circle(self.image, WHITE, (int(base_x + (15*dir_x)), int(base_y - 35)), 8 + int(math.sin(self.anim_timer*5)*4))
            pygame.draw.circle(self.image, self.color_gem, (int(base_x + (15*dir_x)), int(base_y - 35)), 6)
            
        else:
            staff_top_x = base_x + (15 * dir_x)
            staff_top_y = base_y - 20 + staff_y_offset
            staff_bot_x = base_x + (5 * dir_x)
            staff_bot_y = base_y + 25 + staff_y_offset
            pygame.draw.line(self.image, self.color_staff, (staff_bot_x, staff_bot_y), (staff_top_x, staff_top_y), 4)
            pygame.draw.circle(self.image, self.color_gem, (int(staff_top_x), int(staff_top_y)), 6)

        pygame.draw.ellipse(self.image, self.color_team, (base_x - 15, 75, 30, 8), 2)

    def update_particles(self, screen):
        for particle in self.heal_particles[:]:
            particle['timer'] -= 5
            particle['pos'][1] -= 1.5 
            if particle['timer'] <= 0:
                self.heal_particles.remove(particle)
            else:
                alpha = max(0, particle['timer'])
                px, py = int(particle['pos'][0]), int(particle['pos'][1])
                cross_surf = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.rect(cross_surf, (100, 255, 150, alpha), (5, 0, 4, 14)) 
                pygame.draw.rect(cross_surf, (100, 255, 150, alpha), (0, 5, 14, 4)) 
                screen.blit(cross_surf, (px - 7, py - 7))

    def update(self):
        self.update_states()
        self.apply_physics()
        self.draw_shape()

    def draw_extras(self, screen):
        self.update_particles(screen)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_heal_time < self.heal_cooldown:
            cd_ratio = (current_time - self.last_heal_time) / self.heal_cooldown
            pygame.draw.rect(screen, (50, 50, 50), (self.rect.centerx - 20, self.rect.top - 15, 40, 4))
            pygame.draw.rect(screen, self.color_gem, (self.rect.centerx - 20, self.rect.top - 15, int(40 * cd_ratio), 4))