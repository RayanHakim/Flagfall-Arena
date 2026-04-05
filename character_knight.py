import pygame
import math
import random
from character_base import Character
from setting import *

class Knight(Character):
    def __init__(self, x, y, team):
        super().__init__(x, y, team)
        
        self.max_hp = 150
        self.hp = self.max_hp
        self.attack_power = 15
        
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        self.base_max_speed = 4.5
        self.max_speed = self.base_max_speed
        self.acceleration = 0.8  
        self.friction = -0.18    
        
        self.state = "IDLE"
        self.facing = "RIGHT"
        self.anim_timer = 0
        self.anim_speed = 0.10 
        
        self.width = 90  
        self.height = 90
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        self.is_attacking = False
        self.attack_duration = 400 
        self.attack_start_time = 0
        
        self.is_defending = False

        # Skill G: Boomerang Shield
        self.is_throwing = False
        self.shield_out = False # Menandakan perisai sedang melayang di udara
        self.last_throw_time = -3000
        self.throw_cooldown = 3000
        
        self.is_charging = False
        self.charge_speed = 15.0
        self.charge_duration = 400 
        self.charge_start_time = 0
        self.charge_cooldown = 5000 
        self.last_charge_time = -5000
        
        self.dust_particles = []
        
        self.color_plate_light = (200, 205, 210)
        self.color_plate_mid = (150, 155, 160)
        self.color_plate_dark = (90, 95, 100)
        self.color_trim = (218, 165, 32)
        self.color_plume = (200, 40, 40)
        self.color_team = BLUE if team == "PLAYER" else RED

    def move(self, dx, dy):
        if self.state in ["ATTACK", "CHARGE"]:
            return 
            
        self.acc.x = dx * self.acceleration
        self.acc.y = dy * self.acceleration
        
        if dx > 0: self.facing = "RIGHT"
        elif dx < 0: self.facing = "LEFT"
        
        if dx != 0 or dy != 0:
            if not self.is_defending:
                self.state = "RUN"
        else:
            if not self.is_defending:
                self.state = "IDLE"

    def apply_physics(self):
        if self.state == "CHARGE":
            pass 
        else:
            self.acc.x += self.vel.x * self.friction
            self.acc.y += self.vel.y * self.friction
            self.vel += self.acc
            
            if self.vel.length() > self.max_speed:
                self.vel.scale_to_length(self.max_speed)
                
            if self.vel.length() < 0.5 and self.acc.length() < 0.1:
                self.vel.x = 0
                self.vel.y = 0
                if not self.is_defending:
                    self.state = "IDLE"
                
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.acc = pygame.math.Vector2(0, 0)

    def action_melee(self):
        current_time = pygame.time.get_ticks()
        if not self.is_attacking and not self.is_charging and not self.is_defending:
            self.state = "ATTACK"
            self.is_attacking = True
            self.attack_start_time = current_time

    def action_ranged(self):
        """Skill G: Melempar Perisai (Boomerang)"""
        current_time = pygame.time.get_ticks()
        # Hanya bisa melempar jika cooldown selesai dan perisai sedang ada di tangan
        if current_time - self.last_throw_time >= self.throw_cooldown and not self.shield_out:
            if not self.is_attacking and not self.is_charging:
                self.shield_out = True
                self.last_throw_time = current_time
                return "knight_shield" 
        return None

    def action_defense(self):
        # Tidak bisa defensif jika perisai sedang dilempar
        if not self.is_attacking and not self.is_charging and not self.shield_out:
            self.is_defending = not self.is_defending
            if self.is_defending:
                self.state = "DEFEND"
                self.max_speed = self.base_max_speed * 0.4 
            else:
                self.state = "IDLE"
                self.max_speed = self.base_max_speed

    def action_ultimate(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_charge_time >= self.charge_cooldown:
            if not self.is_charging:
                self.state = "CHARGE"
                self.is_charging = True
                self.is_defending = False 
                self.max_speed = self.base_max_speed
                self.charge_start_time = current_time
                self.last_charge_time = current_time
                charge_dir = 1 if self.facing == "RIGHT" else -1
                self.vel = pygame.math.Vector2(charge_dir * self.charge_speed, 0)

    def update_states(self):
        current_time = pygame.time.get_ticks()
        if self.is_attacking:
            if current_time - self.attack_start_time >= self.attack_duration:
                self.is_attacking = False
                self.state = "IDLE"
                
        if self.is_charging:
            if random.random() > 0.3:
                dir_x = 1 if self.facing == "RIGHT" else -1
                self.dust_particles.append({
                    'pos': [self.pos.x - (25 * dir_x), self.pos.y + 30],
                    'radius': random.randint(8, 15),
                    'timer': 255
                })
            if current_time - self.charge_start_time >= self.charge_duration:
                self.is_charging = False
                self.state = "IDLE"
                self.vel = pygame.math.Vector2(0, 0)

    def draw_shape(self):
        self.image.fill((0, 0, 0, 0))
        self.anim_timer += self.anim_speed
        
        breathe = math.sin(self.anim_timer) * 1.5 if self.state == "IDLE" else 0
        run_bob = abs(math.sin(self.anim_timer * 2)) * 3 if self.state == "RUN" else 0
        
        base_y = 45 + breathe - run_bob
        base_x = 45
        dir_x = 1 if self.facing == "RIGHT" else -1

        if self.state in ["DEFEND", "CHARGE"]:
            base_x += 6 * dir_x
            base_y += 4

        # KAKI
        if self.state == "RUN":
            leg1_y = math.cos(self.anim_timer * 2) * 8
            leg2_y = math.cos(self.anim_timer * 2 + math.pi) * 8
            pygame.draw.polygon(self.image, self.color_plate_dark, [(base_x-15, base_y+10), (base_x-5, base_y+10), (base_x-7, base_y+25+leg1_y), (base_x-17, base_y+25+leg1_y)])
            pygame.draw.polygon(self.image, self.color_plate_dark, [(base_x+5, base_y+10), (base_x+15, base_y+10), (base_x+17, base_y+25+leg2_y), (base_x+7, base_y+25+leg2_y)])
        else:
            pygame.draw.polygon(self.image, self.color_plate_dark, [(base_x-15, base_y+10), (base_x-5, base_y+10), (base_x-7, base_y+30), (base_x-17, base_y+30)])
            pygame.draw.polygon(self.image, self.color_plate_dark, [(base_x+5, base_y+10), (base_x+15, base_y+10), (base_x+17, base_y+30), (base_x+7, base_y+30)])

        # TASSETS
        tasset_pts = [(base_x - 18, base_y + 5), (base_x + 18, base_y + 5), (base_x + 22, base_y + 15), (base_x - 22, base_y + 15)]
        pygame.draw.polygon(self.image, self.color_plate_mid, tasset_pts)

        # TORSO
        torso_pts = [(base_x - 16, base_y - 15), (base_x + 16, base_y - 15), (base_x + (18 * dir_x), base_y - 5), (base_x + 15, base_y + 5), (base_x - 15, base_y + 5)]
        pygame.draw.polygon(self.image, self.color_plate_light, torso_pts)
        pygame.draw.polygon(self.image, self.color_trim, torso_pts, 2)
        
        pygame.draw.ellipse(self.image, self.color_plate_mid, (base_x - 22, base_y - 18, 16, 12))
        pygame.draw.ellipse(self.image, self.color_plate_mid, (base_x + 6, base_y - 18, 16, 12))

        # HELM
        head_x, head_y = base_x + (3 * dir_x), base_y - 22
        pygame.draw.polygon(self.image, self.color_plume, [(head_x, head_y - 10), (head_x - (15*dir_x) - run_bob, head_y - 18), (head_x - (8*dir_x), head_y - 5)])
        helm_pts = [(head_x - 10, head_y - 12), (head_x + 10, head_y - 12), (head_x + 12, head_y + 3), (head_x - 12, head_y + 3)]
        pygame.draw.polygon(self.image, self.color_plate_mid, helm_pts)
        pygame.draw.line(self.image, (20,20,20), (head_x + (5*dir_x), head_y - 6), (head_x + (5*dir_x), head_y + 1), 3)
        pygame.draw.line(self.image, (20,20,20), (head_x - 4 + (2*dir_x), head_y - 3), (head_x + 12 + (2*dir_x), head_y - 3), 3)

        # PEDANG
        if self.state == "ATTACK":
            progress = (pygame.time.get_ticks() - self.attack_start_time) / self.attack_duration
            angle = -math.pi/2 + (progress * math.pi)
            if self.facing == "LEFT": angle = math.pi - angle
            sword_end_x = base_x + math.cos(angle) * 45
            sword_end_y = base_y + math.sin(angle) * 45
            pygame.draw.line(self.image, (80,40,20), (base_x, base_y), (base_x + math.cos(angle)*8, base_y + math.sin(angle)*8), 5)
            pygame.draw.polygon(self.image, (230,235,240), [(base_x + math.cos(angle)*10 - math.sin(angle)*4, base_y + math.sin(angle)*10 + math.cos(angle)*4), (base_x + math.cos(angle)*10 + math.sin(angle)*4, base_y + math.sin(angle)*10 - math.cos(angle)*4), (sword_end_x, sword_end_y)])
        else:
            sword_end_x, sword_end_y = base_x + (15 * dir_x), base_y - 30 
            if self.state in ["DEFEND", "CHARGE"]: sword_end_x, sword_end_y = base_x + (30 * dir_x), base_y 
            pygame.draw.line(self.image, (80,40,20), (base_x, base_y), (base_x + (5*dir_x), base_y - 3), 5)
            pygame.draw.polygon(self.image, (230,235,240), [(base_x + (4*dir_x), base_y - 6), (base_x + (8*dir_x), base_y - 2), (sword_end_x, sword_end_y)])

        # PERISAI (Hanya digambar jika shield_out == False)
        if not self.shield_out:
            shield_x, shield_y = base_x + (12 * dir_x), base_y - 8
            if self.state in ["DEFEND", "CHARGE"]: shield_x, shield_y = base_x + (20 * dir_x), base_y - 2
            shield_pts = [(shield_x - (6 * dir_x), shield_y - 15), (shield_x + (10 * dir_x), shield_y - 15), (shield_x + (10 * dir_x), shield_y + 15), (shield_x, shield_y + 25), (shield_x - (6 * dir_x), shield_y + 15)]
            pygame.draw.polygon(self.image, self.color_plate_dark, shield_pts)
            pygame.draw.polygon(self.image, self.color_trim, shield_pts, 3) 
            pygame.draw.line(self.image, self.color_plume, (shield_x + (2*dir_x), shield_y - 10), (shield_x + (2*dir_x), shield_y + 15), 3)
            pygame.draw.line(self.image, self.color_plume, (shield_x - (4*dir_x), shield_y), (shield_x + (8*dir_x), shield_y), 3)

        pygame.draw.ellipse(self.image, self.color_team, (base_x - 20, base_y + 35, 40, 10), 2)

    def update_particles(self, screen):
        for particle in self.dust_particles[:]:
            particle['timer'] -= 10
            particle['radius'] += 0.5 
            particle['pos'][1] -= 0.5 
            if particle['timer'] <= 0:
                self.dust_particles.remove(particle)
            else:
                alpha = max(0, particle['timer'])
                dust_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(dust_surf, (150, 130, 100, alpha), (15, 15), int(particle['radius']))
                screen.blit(dust_surf, (int(particle['pos'][0] - 15), int(particle['pos'][1] - 15)))

    def update(self):
        self.update_states()
        self.apply_physics()
        self.draw_shape()

    def draw_extras(self, screen):
        self.update_particles(screen)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_charge_time < self.charge_cooldown:
            cd_ratio = (current_time - self.last_charge_time) / self.charge_cooldown
            pygame.draw.rect(screen, (50, 50, 50), (self.rect.centerx - 25, self.rect.top - 10, 50, 4))
            pygame.draw.rect(screen, YELLOW, (self.rect.centerx - 25, self.rect.top - 10, int(50 * cd_ratio), 4))