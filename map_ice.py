import pygame
import math
import random
from setting import *

class SnowFlake:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.x = random.randint(0, map_width)
        self.y = random.randint(0, map_height)
        self.speed_y = random.uniform(1.0, 2.5)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.size = random.randint(2, 4)

    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        if self.y > self.map_height:
            self.y = -10
            self.x = random.randint(0, self.map_width)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255, 180), (int(self.x), int(self.y)), self.size)

class MapIce:
    def __init__(self):
        self.name = "Frozen Floating Peak"
        
        # Ukuran Arena Raksasa
        self.map_width = 2500
        self.map_height = 1200
        
        # Warna Langit Kutub (Biru Tua ke Ungu Aurora)
        self.sky_color_top = (10, 20, 40)
        self.sky_color_bot = (30, 60, 100)
        
        self.walkable_areas = []
        self.snowflakes = [SnowFlake(self.map_width, self.map_height) for _ in range(100)]
        self.anim_timer = 0
        
        self.static_canvas = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        self.render_static_world()

    def draw_igloo(self, surface, x, y, scale=1.0):
        """Menggambar Iglo dengan detail blok es"""
        c_igloo = (240, 250, 255)
        c_line = (180, 210, 230)
        r = int(50 * scale)
        
        # Kubah Utama
        pygame.draw.circle(surface, c_igloo, (x, y), r)
        pygame.draw.circle(surface, c_line, (x, y), r, 2)
        
        # Lantai Iglo (biar rata bawahnya)
        pygame.draw.rect(surface, (200, 230, 250), (x - r, y, r*2, r//2)) # Background pulau
        
        # Garis blok es (Horizontal)
        for i in range(1, 4):
            h = y - (i * (r // 4))
            w_offset = math.sqrt(max(0, r**2 - (y-h)**2))
            pygame.draw.line(surface, c_line, (int(x - w_offset), h), (int(x + w_offset), h), 1)
            
        # Pintu Masuk
        door_w, door_h = int(25 * scale), int(30 * scale)
        pygame.draw.rect(surface, (150, 180, 210), (x - door_w//2, y - door_h + 10, door_w, door_h), border_radius=5)
        pygame.draw.rect(surface, c_line, (x - door_w//2, y - door_h + 10, door_w, door_h), 2, border_radius=5)

    def draw_ice_pillar(self, surface, x, y, scale=1.0):
        """Kristal Es runcing"""
        pts = [(x, y), (x - 15*scale, y - 20*scale), (x, y - 60*scale), (x + 15*scale, y - 20*scale)]
        pygame.draw.polygon(surface, (180, 230, 255), pts)
        pygame.draw.polygon(surface, (255, 255, 255, 150), pts, 2)

    def draw_frozen_island(self, surface, cx, cy, rx, ry, irregularity, depth, team="neutral"):
        segments = 30
        angle_step = (math.pi * 2) / segments
        top_poly = []
        for i in range(segments):
            angle = i * angle_step
            noise = random.uniform(-irregularity, irregularity)
            top_poly.append((cx + math.cos(angle)*(rx+noise), cy + math.sin(angle)*(ry+noise)))
        
        self.walkable_areas.append(top_poly)
        
        # Bagian Bawah Pulau (Es Biru Tua 3D)
        bottom_poly = [(x, y + depth) for x, y in top_poly]
        ice_dark = (60, 100, 150)
        ice_mid = (100, 150, 200)
        
        pygame.draw.polygon(surface, ice_dark, bottom_poly)
        for i in range(len(top_poly)):
            p1, p2 = top_poly[i], top_poly[(i+1)%len(top_poly)]
            b1, b2 = bottom_poly[i], bottom_poly[(i+1)%len(top_poly)]
            color = ice_mid if i % 2 == 0 else ice_dark
            pygame.draw.polygon(surface, color, [p1, p2, b2, b1])

        # Permukaan Salju
        snow_color = (240, 250, 255)
        if team == "blue_base": snow_color = (200, 230, 255) # Salju kebiruan
        if team == "red_base": snow_color = (255, 220, 220)  # Salju kemerahan
        pygame.draw.polygon(surface, snow_color, top_poly)
        
        # Efek Kilau Es
        for _ in range(int(rx * ry / 500)):
            px = cx + random.randint(int(-rx), int(rx))
            py = cy + random.randint(int(-ry), int(ry))
            pygame.draw.circle(surface, (255, 255, 255), (px, py), random.randint(1, 3))

    def draw_ice_bridge(self, surface, start, end):
        sx, sy = start
        ex, ey = end
        dist = math.hypot(ex-sx, ey-sy)
        planks = int(dist / 25)
        for i in range(planks + 1):
            t = i / planks
            px = sx + (ex-sx)*t
            py = sy + (ey-sy)*t + math.sin(t*math.pi)*20
            # Balok Es Jembatan
            rect = pygame.Rect(px-40, py, 80, 20)
            pygame.draw.rect(surface, (150, 200, 255), rect, border_radius=3)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=3)

    def render_static_world(self):
        # 1. BASE UTAMA
        self.draw_frozen_island(self.static_canvas, 350, 600, 280, 220, 20, 120, "blue_base")
        self.draw_frozen_island(self.static_canvas, self.map_width-350, 600, 280, 220, 20, 120, "red_base")
        
        # 2. LANE
        self.draw_frozen_island(self.static_canvas, self.map_width//2, 250, 550, 130, 15, 90) # Top
        self.draw_frozen_island(self.static_canvas, self.map_width//2, 950, 550, 130, 15, 90) # Bot
        self.draw_frozen_island(self.static_canvas, self.map_width//2, 600, 180, 180, 30, 70) # Mid
        
        # 3. JEMBATAN ES
        self.draw_ice_bridge(self.static_canvas, (550, 500), (self.map_width//2-400, 250)) # Blue to Top
        self.draw_ice_bridge(self.static_canvas, (550, 700), (self.map_width//2-400, 950)) # Blue to Bot
        self.draw_ice_bridge(self.static_canvas, (self.map_width-550, 500), (self.map_width//2+400, 250)) # Red to Top
        self.draw_ice_bridge(self.static_canvas, (self.map_width-550, 700), (self.map_width//2+400, 950)) # Red to Bot

        # 4. DEKORASI (Iglo & Kristal)
        self.draw_igloo(self.static_canvas, 300, 550, 1.2) # Iglo di Base Biru
        self.draw_igloo(self.static_canvas, self.map_width-300, 550, 1.2) # Iglo di Base Merah
        self.draw_igloo(self.static_canvas, self.map_width//2, 580, 0.9) # Iglo Tengah
        
        for _ in range(20):
            self.draw_ice_pillar(self.static_canvas, random.randint(800, 1700), random.randint(200, 1000), random.uniform(0.5, 1.5))

    def update(self):
        self.anim_timer += 0.02
        for s in self.snowflakes: s.update()

    def draw(self, screen, camera_x, camera_y):
        view_surf = pygame.Surface((WIDTH, HEIGHT))
        
        # 1. Langit Parallax
        sky = pygame.Surface((self.map_width, self.map_height))
        for y in range(self.map_height):
            progress = y / self.map_height
            col = [self.sky_color_top[i]*(1-progress) + self.sky_color_bot[i]*progress for i in range(3)]
            pygame.draw.line(sky, col, (0, y), (self.map_width, y))
        view_surf.blit(sky, (-camera_x * 0.2, -camera_y * 0.2))
        
        # 2. Dunia Utama (Floating)
        float_y = math.sin(self.anim_timer) * 12
        view_surf.blit(self.static_canvas, (-camera_x, -camera_y + int(float_y)))
        
        # 3. Salju Jatuh (Overlay)
        snow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for s in self.snowflakes:
            # Render salju relatif terhadap layar
            sx = (s.x - camera_x) % self.map_width
            sy = (s.y - camera_y) % self.map_height
            if 0 <= sx <= WIDTH and 0 <= sy <= HEIGHT:
                pygame.draw.circle(snow_surf, (255, 255, 255, 200), (int(sx), int(sy)), s.size)
        view_surf.blit(snow_surf, (0,0))
        
        screen.blit(view_surf, (0,0))