import pygame
import math
import random
from setting import *

class Cloud:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.x = random.randint(0, map_width)
        self.y = random.randint(0, map_height)
        self.speed = random.uniform(0.3, 1.0)
        self.scale = random.uniform(0.5, 2.0)
        self.image = self.create_cloud()

    def create_cloud(self):
        surf = pygame.Surface((200 * self.scale, 100 * self.scale), pygame.SRCALPHA)
        circles = [
            (50, 50, 40), (100, 40, 50), (150, 50, 40), 
            (80, 60, 35), (120, 60, 35)
        ]
        for cx, cy, r in circles:
            pygame.draw.circle(surf, (255, 255, 255, 40), (int(cx * self.scale), int(cy * self.scale)), int(r * self.scale))
            pygame.draw.circle(surf, (240, 245, 255, 80), (int(cx * self.scale), int((cy - 5) * self.scale)), int(r * self.scale * 0.9))
        return surf

    def update(self):
        self.x -= self.speed
        if self.x < -300:
            self.x = self.map_width + 200
            self.y = random.randint(0, self.map_height)

    def draw(self, surface):
        surface.blit(self.image, (int(self.x), int(self.y)))


class Firefly:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.x = random.randint(100, map_width - 100)
        self.y = random.randint(100, map_height - 100)
        self.base_y = self.y
        self.speed_x = random.uniform(-0.8, 0.8)
        self.timer = random.uniform(0, math.pi * 2)
        self.size = random.randint(1, 4)

    def update(self):
        self.x += self.speed_x
        self.timer += 0.05
        self.y = self.base_y + math.sin(self.timer) * 15
        if self.x < 0 or self.x > self.map_width:
            self.speed_x *= -1

    def draw(self, surface):
        glow_radius = self.size * 3 + math.sin(self.timer * 2) * 2
        if glow_radius > 0:
            surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (150, 255, 50, 30), (glow_radius, glow_radius), glow_radius)
            pygame.draw.circle(surf, (200, 255, 150, 150), (glow_radius, glow_radius), self.size)
            surface.blit(surf, (int(self.x - glow_radius), int(self.y - glow_radius)))


class MapForest:
    def __init__(self):
        self.name = "Floating Mystic Forest"
        
        # MAP LEBIH LUAS DARI LAYAR (Scrolable Arena)
        self.map_width = 2500
        self.map_height = 1200
        
        self.sky_color_top = (15, 25, 45)
        self.sky_color_bot = (60, 90, 120)
        
        # Area Poligon Tanah (Untuk sistem tabrakan/pijakan karakter nanti)
        self.walkable_areas = []
        
        self.clouds = [Cloud(self.map_width, self.map_height) for _ in range(25)]
        self.fireflies = [Firefly(self.map_width, self.map_height) for _ in range(60)]
        
        self.anim_timer = 0
        
        # Kanvas Raksasa untuk Background Statis
        self.static_canvas = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        self.render_static_world()

    def generate_island_polygon(self, cx, cy, rx, ry, irregularity):
        """Membuat poligon elips tak beraturan (bisa lonjong panjang)"""
        points = []
        segments = 40
        angle_step = (math.pi * 2) / segments
        for i in range(segments):
            angle = i * angle_step
            # Noise agar pinggiran tanah tidak rata sempurna
            noise = random.uniform(-irregularity, irregularity)
            px = cx + math.cos(angle) * (rx + noise)
            py = cy + math.sin(angle) * (ry + noise)
            points.append((px, py))
        return points

    def draw_floating_island(self, surface, cx, cy, rx, ry, irregularity, depth, island_type="neutral"):
        top_poly = self.generate_island_polygon(cx, cy, rx, ry, irregularity)
        self.walkable_areas.append(top_poly) # Simpan kordinat tanah pijakan
        
        bottom_poly = [(x, y + depth) for x, y in top_poly]
        
        dirt_color = (50, 35, 20)
        dirt_shadow = (30, 20, 10)
        
        # Gambar Dasar/Akar
        pygame.draw.polygon(surface, dirt_shadow, bottom_poly)
        
        # Gambar Dinding Tanah 3D
        for i in range(len(top_poly)):
            p1 = top_poly[i]
            p2 = top_poly[(i + 1) % len(top_poly)]
            b1 = bottom_poly[i]
            b2 = bottom_poly[(i + 1) % len(top_poly)]
            wall_color = dirt_color if i % 2 == 0 else dirt_shadow
            pygame.draw.polygon(surface, wall_color, [p1, p2, b2, b1])

        # Overhang Rumput
        grass_rim_poly = [(x, y + 12) for x, y in top_poly]
        pygame.draw.polygon(surface, (20, 80, 20), grass_rim_poly)
        
        # Permukaan Tanah
        grass_color = (34, 120, 34)
        if island_type == "blue_base": grass_color = (30, 100, 130) # Rumput agak kebiruan
        if island_type == "red_base": grass_color = (130, 40, 40)   # Rumput agak kemerahan
        
        pygame.draw.polygon(surface, grass_color, top_poly)
        
        # Tekstur Rumput
        for _ in range(int(rx * ry / 200)):
            px = cx + random.randint(int(-rx), int(rx))
            py = cy + random.randint(int(-ry), int(ry))
            
            # Cek apakah titik ada di dalam elips
            if ((px-cx)**2 / rx**2) + ((py-cy)**2 / ry**2) <= 1:
                col = (40, 150, 40) if island_type == "neutral" else (60, 140, 160) if island_type == "blue_base" else (160, 60, 60)
                pygame.draw.circle(surface, col, (px, py), random.randint(2, 6))

        return top_poly

    def draw_bridge(self, surface, start_pos, end_pos):
        sx, sy = start_pos
        ex, ey = end_pos
        dx = ex - sx
        dy = ey - sy
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        
        plank_width = 25
        plank_length = 80
        planks = int(dist / 30)
        
        for i in range(planks + 1):
            progress = i / planks
            px = sx + dx * progress
            py = sy + dy * progress
            sag = math.sin(progress * math.pi) * 30 # Jembatan gantung melengkung parah
            py += sag
            
            cos_a = math.cos(angle + math.pi/2)
            sin_a = math.sin(angle + math.pi/2)
            
            p1 = (px + cos_a * plank_length/2, py + sin_a * plank_length/2)
            p2 = (px - cos_a * plank_length/2, py - sin_a * plank_length/2)
            p3 = (p2[0], p2[1] + plank_width)
            p4 = (p1[0], p1[1] + plank_width)
            
            pygame.draw.polygon(surface, (30, 15, 5), [(x, y+8) for x, y in [p1, p2, p3, p4]])
            pygame.draw.polygon(surface, (90, 50, 20), [p1, p2, p3, p4])
            pygame.draw.line(surface, (120, 70, 30), p1, p2, 3)

    def draw_tree(self, surface, x, y, scale=1.0):
        trunk_w = 25 * scale
        trunk_h = 80 * scale
        pygame.draw.rect(surface, (40, 20, 10), (x - trunk_w/2, y - trunk_h, trunk_w, trunk_h))
        
        leaves = [(0, -trunk_h - 20, 55), (-35, -trunk_h + 10, 45), (35, -trunk_h + 10, 45), (0, -trunk_h + 30, 50)]
        for lx, ly, lr in leaves:
            px, py, pr = int(x + lx * scale), int(y + ly * scale), int(lr * scale)
            pygame.draw.circle(surface, (10, 50, 20), (px, py + 8), pr)
            pygame.draw.circle(surface, (25, 90, 25), (px, py), pr)
            pygame.draw.circle(surface, (40, 120, 40), (px - int(pr*0.2), py - int(pr*0.2)), int(pr*0.7))

    def render_static_world(self):
        """Merender struktur 5 pulau utama CTF MOBA"""
        
        # 1. BASE KIRI (Tim Biru)
        blue_base = (300, self.map_height // 2)
        self.draw_floating_island(self.static_canvas, blue_base[0], blue_base[1], 250, 200, 20, 100, "blue_base")
        
        # 2. BASE KANAN (Tim Merah)
        red_base = (self.map_width - 300, self.map_height // 2)
        self.draw_floating_island(self.static_canvas, red_base[0], red_base[1], 250, 200, 20, 100, "red_base")
        
        # 3. JALUR ATAS (Top Lane - Panjang membetang)
        top_lane = (self.map_width // 2, 250)
        self.draw_floating_island(self.static_canvas, top_lane[0], top_lane[1], 500, 120, 15, 80)
        
        # 4. JALUR BAWAH (Bottom Lane - Panjang membentang)
        bot_lane = (self.map_width // 2, self.map_height - 250)
        self.draw_floating_island(self.static_canvas, bot_lane[0], bot_lane[1], 500, 120, 15, 80)
        
        # 5. AREA TENGAH (Mid Jungle)
        mid_area = (self.map_width // 2, self.map_height // 2)
        self.draw_floating_island(self.static_canvas, mid_area[0], mid_area[1], 150, 150, 30, 60)

        # JEMBATAN PENGHUBUNG (Membentuk jalur)
        # Base Kiri ke Top, Mid, Bot
        self.draw_bridge(self.static_canvas, (blue_base[0]+150, blue_base[1]-100), (top_lane[0]-350, top_lane[1]))
        self.draw_bridge(self.static_canvas, (blue_base[0]+200, blue_base[1]), (mid_area[0]-120, mid_area[1]))
        self.draw_bridge(self.static_canvas, (blue_base[0]+150, blue_base[1]+100), (bot_lane[0]-350, bot_lane[1]))
        
        # Base Kanan ke Top, Mid, Bot
        self.draw_bridge(self.static_canvas, (red_base[0]-150, red_base[1]-100), (top_lane[0]+350, top_lane[1]))
        self.draw_bridge(self.static_canvas, (red_base[0]-200, red_base[1]), (mid_area[0]+120, mid_area[1]))
        self.draw_bridge(self.static_canvas, (red_base[0]-150, red_base[1]+100), (bot_lane[0]+350, bot_lane[1]))

        # Tambahkan ornamen hutan di sepanjang Top dan Bot lane
        for _ in range(15):
            self.draw_tree(self.static_canvas, top_lane[0] + random.randint(-400, 400), top_lane[1] - random.randint(20, 80), random.uniform(0.7, 1.2))
            self.draw_tree(self.static_canvas, bot_lane[0] + random.randint(-400, 400), bot_lane[1] + random.randint(20, 80), random.uniform(0.7, 1.2))

        # Tanda Area Base
        pygame.draw.circle(self.static_canvas, (0, 100, 255, 100), blue_base, 80, 5) # Zona Bendera Biru
        pygame.draw.circle(self.static_canvas, (255, 50, 0, 100), red_base, 80, 5)   # Zona Bendera Merah

    def draw_sky_gradient(self, surface, screen_height):
        # Gradasi digambar di kanvas raksasa
        for y in range(self.map_height):
            progress = y / self.map_height
            r = int(self.sky_color_top[0] * (1 - progress) + self.sky_color_bot[0] * progress)
            g = int(self.sky_color_top[1] * (1 - progress) + self.sky_color_bot[1] * progress)
            b = int(self.sky_color_top[2] * (1 - progress) + self.sky_color_bot[2] * progress)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.map_width, y))

    def update(self):
        self.anim_timer += 0.02
        for cloud in self.clouds: cloud.update()
        for firefly in self.fireflies: firefly.update()

    def draw(self, screen, camera_x, camera_y):
        """
        PENTING: Menggunakan camera_x dan camera_y untuk MENGGESER peta 
        yang jauh lebih besar dari layar monitor.
        """
        # Bikin surface sementara seluas monitor untuk digambar peta
        view_surf = pygame.Surface((WIDTH, HEIGHT))
        
        # 1. Langit (Ikut geser sedikit / efek Parallax jauh)
        sky_surf = pygame.Surface((self.map_width, self.map_height))
        self.draw_sky_gradient(sky_surf, HEIGHT)
        view_surf.blit(sky_surf, (-camera_x * 0.2, -camera_y * 0.2)) 
        
        # 2. Awan (Parallax tengah)
        cloud_surf = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        for cloud in self.clouds: cloud.draw(cloud_surf)
        view_surf.blit(cloud_surf, (-camera_x * 0.5, -camera_y * 0.5))
        
        # 3. Peta Utama Statis (Tanah & Jembatan)
        float_y = math.sin(self.anim_timer) * 10
        view_surf.blit(self.static_canvas, (-camera_x, -camera_y + int(float_y)))
        
        # 4. Kunang-kunang
        firefly_surf = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        for firefly in self.fireflies: firefly.draw(firefly_surf)
        view_surf.blit(firefly_surf, (-camera_x, -camera_y + int(float_y)))
        
        # Render ke layar monitor sebenarnya
        screen.blit(view_surf, (0,0))