import pygame
import math
import random
from character_base import Character
from setting import *

class Assassin(Character):
    def __init__(self, x, y, team):
        super().__init__(x, y, team)
        
        self.max_hp = 70
        self.hp = self.max_hp
        self.attack_power = 25  
        
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        
        self.max_speed = 6.5
        self.acceleration = 1.2
        self.friction = -0.15 
        
        self.state = "IDLE" 
        self.facing = "RIGHT" 
        
        self.anim_timer = 0
        self.anim_speed = 0.15
        
        self.width = 60
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        self.is_attacking = False
        self.attack_duration = 200 
        self.attack_start_time = 0
        
        self.is_throwing = False
        self.throw_duration = 300
        self.last_throw_time = -2000
        self.throw_cooldown = 1500

        self.is_stealth = False
        self.stealth_duration = 2500
        self.stealth_start_time = 0
        self.stealth_cooldown = 6000
        self.last_stealth_time = -6000
        
        self.is_dashing = False
        self.dash_speed = 25.0
        self.dash_duration = 150 
        self.dash_start_time = 0
        self.dash_cooldown = 3000 
        self.last_dash_time = -3000
        
        self.trail_particles = []
        
        self.color_cloak = (30, 30, 40)       
        self.color_cloak_light = (50, 50, 65) 
        self.color_skin = (255, 200, 150)     
        self.color_eye = (255, 50, 50)        
        self.color_dagger = (200, 200, 200)   
        self.color_team = BLUE if team == "PLAYER" else RED

    def move(self, dx, dy):
        if self.state in ["ATTACK", "DASH", "THROW"]:
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
        if self.state == "DASH":
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
                if self.state not in ["ATTACK", "THROW"]: self.state = "IDLE"
                
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.acc = pygame.math.Vector2(0, 0)

    def action_melee(self):
        current_time = pygame.time.get_ticks()
        if not self.is_attacking and not self.is_dashing:
            self.state = "ATTACK"
            self.is_attacking = True
            self.attack_start_time = current_time
            self.is_stealth = False 

    def action_ranged(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_throw_time >= self.throw_cooldown:
            if not self.is_attacking and not self.is_dashing:
                self.state = "THROW"
                self.is_throwing = True
                self.attack_start_time = current_time 
                self.last_throw_time = current_time
                self.is_stealth = False
                return "dagger"

    def action_defense(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_stealth_time >= self.stealth_cooldown:
            self.is_stealth = True
            self.stealth_start_time = current_time
            self.last_stealth_time = current_time

    def action_ultimate(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dash_time >= self.dash_cooldown:
            if not self.is_dashing:
                self.state = "DASH"
                self.is_dashing = True
                self.dash_start_time = current_time
                self.last_dash_time = current_time
                dash_dir = 1 if self.facing == "RIGHT" else -1
                self.vel = pygame.math.Vector2(dash_dir * self.dash_speed, 0)
                self.is_stealth = False

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

        if self.is_stealth:
            if current_time - self.stealth_start_time >= self.stealth_duration:
                self.is_stealth = False
                
        if self.is_dashing:
            self.trail_particles.append({
                'pos': (int(self.pos.x), int(self.pos.y)),
                'alpha': 200,
                'facing': self.facing
            })
            if current_time - self.dash_start_time >= self.dash_duration:
                self.is_dashing = False
                self.state = "IDLE"
                self.vel = pygame.math.Vector2(0, 0)

    def draw_shape(self):
        self.image.fill((0, 0, 0, 0)) 
        self.anim_timer += self.anim_speed
        
        breathe = math.sin(self.anim_timer) * 2 if self.state == "IDLE" else 0
        run_bob = abs(math.sin(self.anim_timer * 2)) * 5 if self.state == "RUN" else 0
        lunge = 8 if self.state == "ATTACK" else 0
        if self.facing == "LEFT": lunge = -lunge
        
        base_y = 30 + breathe - run_bob
        base_x = 30 + lunge
        dir_x = 1 if self.facing == "RIGHT" else -1

        alpha_val = 80 if self.is_stealth else 255

        # KAKI
        leg_color = (20, 20, 25)
        if self.state == "RUN":
            leg1 = math.cos(self.anim_timer * 2) * 10
            leg2 = math.cos(self.anim_timer * 2 + math.pi) * 10
            pygame.draw.rect(self.image, (*leg_color, alpha_val), (base_x - 5, base_y + 10, 8, 15 + leg1), border_radius=3)
            pygame.draw.rect(self.image, (*leg_color, alpha_val), (base_x + 2, base_y + 10, 8, 15 + leg2), border_radius=3)
        else:
            pygame.draw.rect(self.image, (*leg_color, alpha_val), (base_x - 6, base_y + 10, 8, 18), border_radius=3)
            pygame.draw.rect(self.image, (*leg_color, alpha_val), (base_x + 4, base_y + 10, 8, 18), border_radius=3)

        # JUBAH
        cape_pts = [
            (base_x - (12 * dir_x), base_y - 15), (base_x + (8 * dir_x), base_y - 15),
            (base_x + (10 * dir_x), base_y + 12), (base_x - (15 * dir_x), base_y + 15),
            (base_x - (20 * dir_x) - (run_bob*dir_x), base_y + 5)
        ]
        pygame.draw.polygon(self.image, (*self.color_cloak, alpha_val), cape_pts)
        
        # KEPALA
        head_x, head_y = base_x + (3 * dir_x), base_y - 18
        # Tudung Luar
        pygame.draw.circle(self.image, (*self.color_cloak, alpha_val), (int(head_x), int(head_y)), 12)
        # Kulit Wajah
        pygame.draw.circle(self.image, (*self.color_skin, alpha_val), (int(head_x), int(head_y)), 10)
        
        # MASKER HITAM (DIPERLEBAR: Menutupi seluruh bagian bawah wajah)
        mask_w, mask_h = 20, 11
        mask_rect = pygame.Rect(int(head_x - 10), int(head_y - 1), mask_w, mask_h)
        pygame.draw.rect(self.image, (10, 10, 15, alpha_val), mask_rect, border_bottom_left_radius=10, border_bottom_right_radius=10)
        
        # MATA MERAH (Posisi disesuaikan di atas masker)
        eye_y = head_y - 3
        pygame.draw.circle(self.image, (*self.color_eye, alpha_val), (int(head_x + 4 * dir_x), int(eye_y)), 2)
        pygame.draw.line(self.image, (*self.color_eye, alpha_val), (head_x + 2 * dir_x, eye_y), (head_x + 7 * dir_x, eye_y), 2)

        # SENJATA (DAGGER)
        if self.state == "ATTACK":
            ext = math.sin((pygame.time.get_ticks() - self.attack_start_time) / self.attack_duration * math.pi) * 15
            arm_x, arm_y = base_x + ((15 + ext) * dir_x), base_y
            pygame.draw.line(self.image, (*self.color_cloak_light, alpha_val), (base_x, base_y - 8), (arm_x, arm_y), 5)
            pygame.draw.polygon(self.image, (*self.color_dagger, alpha_val), [(arm_x, arm_y-2), (arm_x, arm_y+2), (arm_x+(15*dir_x), arm_y)])
        elif self.state == "THROW":
            arm_x, arm_y = base_x + (20 * dir_x), base_y - 10
            pygame.draw.line(self.image, (*self.color_cloak_light, alpha_val), (base_x, base_y - 8), (arm_x, arm_y), 5)
        else:
            arm_x, arm_y = base_x + (5 * dir_x), base_y + 5
            pygame.draw.line(self.image, (*self.color_cloak_light, alpha_val), (base_x, base_y - 8), (arm_x, arm_y), 5)
            pygame.draw.polygon(self.image, (*self.color_dagger, alpha_val), [(arm_x-2, arm_y), (arm_x+2, arm_y), (arm_x+(10*dir_x), arm_y+10)])

        pygame.draw.ellipse(self.image, (*self.color_team, 100), (base_x - 15, base_y + 25, 30, 8), 2)

    def update_particles(self, screen):
        for particle in self.trail_particles[:]:
            particle['alpha'] -= 20
            if particle['alpha'] <= 0:
                self.trail_particles.remove(particle)
            else:
                s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.circle(s, (50, 50, 70, particle['alpha']), (30, 30), 15)
                screen.blit(s, s.get_rect(center=particle['pos']))

    def update(self):
        self.update_states()
        self.apply_physics()
        self.draw_shape()

    def draw_extras(self, screen):
        self.update_particles(screen)
        
        curr = pygame.time.get_ticks()
        if curr - self.last_dash_time < self.dash_cooldown:
            ratio = (curr - self.last_dash_time) / self.dash_cooldown
            pygame.draw.rect(screen, (50, 50, 50), (self.rect.left, self.rect.top - 25, self.rect.width, 4))
            pygame.draw.rect(screen, YELLOW, (self.rect.left, self.rect.top - 25, int(self.rect.width * ratio), 4))
            
        if self.is_stealth:
            self.draw_text_shadow(screen, "STEALTH", pygame.font.SysFont(None, 20), WHITE, self.rect.centerx - 25, self.rect.top - 45)

    def draw_text_shadow(self, screen, text, font, color, x, y):
        sh = font.render(text, True, BLACK)
        sr = font.render(text, True, color)
        screen.blit(sh, (x+1, y+1))
        screen.blit(sr, (x, y))