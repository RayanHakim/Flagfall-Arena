import pygame
import math
import random
from setting import *

class DustParticle:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.reset()
        self.x = random.randint(0, map_width)

    def reset(self):
        self.x = -50
        self.y = random.randint(0, self.map_height)
        self.vel_x = random.uniform(4.0, 9.0)
        self.vel_y = random.uniform(-1.0, 1.0)
        self.size = random.randint(2, 5)
        self.alpha = random.randint(30, 120)
        self.color = random.choice([(230, 190, 130), (210, 170, 110), (255, 240, 200)])

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        if self.x > self.map_width:
            self.reset()

    def draw(self, surface):
        s = pygame.Surface((self.size * 6, self.size), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*self.color, self.alpha), (0, 0, self.size * 6, self.size))
        surface.blit(s, (int(self.x), int(self.y)))

class MapDesert:
    def __init__(self):
        self.name = "The Forbidden Sunken Sands"
        self.map_width = 2500
        self.map_height = 1200
        
        self.sky_color_top = (255, 140, 0)
        self.sky_color_bot = (255, 240, 150)
        
        self.walkable_areas = []
        self.obstacles = []
        
        self.anim_timer = 0
        self.mirage_timer = 0
        
        self.dust_storm = [DustParticle(self.map_width, self.map_height) for _ in range(150)]
        
        self.static_canvas = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        self.render_static_world()

    def generate_detailed_poly(self, cx, cy, rx, ry, segments, irregularity):
        points = []
        for i in range(segments):
            angle = i * (math.pi * 2 / segments)
            noise = random.uniform(-irregularity, irregularity)
            px = cx + math.cos(angle) * (rx + noise)
            py = cy + math.sin(angle) * (ry + noise)
            points.append((px, py))
        return points

    def draw_sand_dune(self, surface, cx, cy, rx, ry, depth, island_type="neutral"):
        top_poly = self.generate_detailed_poly(cx, cy, rx, ry, 40, 35)
        self.walkable_areas.append(top_poly)
        
        bottom_poly = [(x, y + depth) for x, y in top_poly]
        
        sand_dark = (140, 90, 40)
        sand_mid = (190, 130, 60)
        sand_light = (237, 201, 175)
        
        if island_type == "blue_base": sand_light = (170, 190, 220)
        elif island_type == "red_base": sand_light = (220, 160, 160)

        pygame.draw.polygon(surface, (80, 50, 20), bottom_poly)
        
        for i in range(len(top_poly)):
            p1, p2 = top_poly[i], top_poly[(i+1)%len(top_poly)]
            b1, b2 = bottom_poly[i], bottom_poly[(i+1)%len(top_poly)]
            col = sand_mid if i % 2 == 0 else sand_dark
            pygame.draw.polygon(surface, col, [p1, p2, b2, b1])

        pygame.draw.polygon(surface, sand_light, top_poly)
        
        for _ in range(int(rx * ry / 150)):
            px = cx + random.randint(int(-rx), int(rx))
            py = cy + random.randint(int(-ry), int(ry))
            if ((px-cx)**2 / rx**2) + ((py-cy)**2 / ry**2) <= 0.85:
                col = (210, 170, 120) if island_type == "neutral" else (150, 170, 200) if island_type == "blue_base" else (200, 140, 140)
                pygame.draw.circle(surface, col, (px, py), random.randint(1, 4))

    def draw_bridge(self, surface, start_pos, end_pos):
        sx, sy = start_pos
        ex, ey = end_pos
        dx, dy = ex - sx, ey - sy
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        
        plank_width = 25
        plank_length = 85
        planks = int(dist / 32)
        
        for i in range(planks + 1):
            prog = i / planks
            px = sx + dx * prog
            py = sy + dy * prog
            sag = math.sin(prog * math.pi) * 35 
            py += sag
            
            cos_a = math.cos(angle + math.pi/2)
            sin_a = math.sin(angle + math.pi/2)
            
            p1 = (px + cos_a * plank_length/2, py + sin_a * plank_length/2)
            p2 = (px - cos_a * plank_length/2, py - sin_a * plank_length/2)
            p3 = (p2[0], p2[1] + plank_width)
            p4 = (p1[0], p1[1] + plank_width)
            
            pygame.draw.polygon(surface, (50, 30, 10), [(x, y+6) for x, y in [p1, p2, p3, p4]])
            pygame.draw.polygon(surface, (139, 90, 43), [p1, p2, p3, p4])
            pygame.draw.line(surface, (160, 110, 60), p1, p2, 3)
            
            pygame.draw.circle(surface, (40, 40, 40), (int(p1[0]), int(p1[1])), 4)
            pygame.draw.circle(surface, (40, 40, 40), (int(p2[0]), int(p2[1])), 4)

    def draw_ancient_pillar(self, surface, x, y):
        w, h = 30, 100
        pygame.draw.rect(surface, (100, 90, 80), (x - w/2, y - h, w, h))
        pygame.draw.rect(surface, (80, 70, 60), (x - w/2, y - h, w/4, h))
        for i in range(3):
            yy = y - h + (i * 30)
            pygame.draw.line(surface, (60, 50, 40), (x - w/2, yy), (x + w/2, yy), 3)
        self.obstacles.append(pygame.Rect(x - w/2, y - 20, w, 20))

    def draw_skeleton(self, surface, x, y):
        col = (220, 220, 210)
        pygame.draw.circle(surface, col, (x, y), 10)
        pygame.draw.line(surface, col, (x, y+10), (x+40, y+15), 5)
        for i in range(4):
            pygame.draw.line(surface, col, (x + 10 + i*8, y+12), (x + 10 + i*8, y-5), 3)

    def draw_oasis(self, surface, x, y):
        pygame.draw.ellipse(surface, (30, 144, 255), (x-100, y-50, 200, 100))
        pygame.draw.ellipse(surface, (0, 191, 255), (x-90, y-40, 180, 80))

    def draw_cactus_complex(self, surface, x, y, scale):
        c_col = (40, 100, 40)
        pygame.draw.rect(surface, c_col, (x-7*scale, y-50*scale, 14*scale, 50*scale), border_radius=7)
        arms = [(-1, 30, 20), (1, 20, 25)]
        for side, h, l in arms:
            ax = x + (7*side*scale)
            ay = y - h*scale
            pygame.draw.rect(surface, c_col, (ax if side > 0 else ax-l*scale, ay, l*scale, 10*scale), border_radius=4)
            pygame.draw.rect(surface, c_col, (ax+l*side*scale-5*scale if side > 0 else ax-l*scale, ay-15*scale, 10*scale, 20*scale), border_radius=5)
        self.obstacles.append(pygame.Rect(x-15, y-15, 30, 30))

    def render_static_world(self):
        blue_base = (350, self.map_height // 2)
        red_base = (self.map_width - 350, self.map_height // 2)
        top_lane = (self.map_width // 2, 220)
        bot_lane = (self.map_width // 2, self.map_height - 220)
        center_island = (self.map_width // 2, self.map_height // 2)

        self.draw_sand_dune(self.static_canvas, blue_base[0], blue_base[1], 350, 280, 130, "blue_base")
        self.draw_sand_dune(self.static_canvas, red_base[0], red_base[1], 350, 280, 130, "red_base")
        self.draw_sand_dune(self.static_canvas, top_lane[0], top_lane[1], 800, 180, 100)
        self.draw_sand_dune(self.static_canvas, bot_lane[0], bot_lane[1], 800, 180, 100)
        self.draw_sand_dune(self.static_canvas, center_island[0], center_island[1], 400, 300, 80)
        self.draw_oasis(self.static_canvas, center_island[0], center_island[1])

        self.draw_bridge(self.static_canvas, (blue_base[0]+180, blue_base[1]-120), (top_lane[0]-450, top_lane[1]))
        self.draw_bridge(self.static_canvas, (blue_base[0]+220, blue_base[1]), (center_island[0]-250, center_island[1]))
        self.draw_bridge(self.static_canvas, (blue_base[0]+180, blue_base[1]+120), (bot_lane[0]-450, bot_lane[1]))
        
        self.draw_bridge(self.static_canvas, (red_base[0]-180, red_base[1]-120), (top_lane[0]+450, top_lane[1]))
        self.draw_bridge(self.static_canvas, (red_base[0]-220, red_base[1]), (center_island[0]+250, center_island[1]))
        self.draw_bridge(self.static_canvas, (red_base[0]-180, red_base[1]+120), (bot_lane[0]+450, bot_lane[1]))

        for _ in range(12):
            self.draw_ancient_pillar(self.static_canvas, random.randint(600, 1900), random.randint(100, 1100))
        for _ in range(8):
            self.draw_skeleton(self.static_canvas, random.randint(400, 2100), random.randint(200, 1000))
        for _ in range(30):
            tx = random.randint(100, self.map_width-100)
            ty = random.randint(100, self.map_height-100)
            self.draw_cactus_complex(self.static_canvas, tx, ty, random.uniform(0.7, 1.4))

    def draw_sky(self, surface):
        for y in range(self.map_height):
            prog = y / self.map_height
            r = int(self.sky_color_top[0]*(1-prog) + self.sky_color_bot[0]*prog)
            g = int(self.sky_color_top[1]*(1-prog) + self.sky_color_bot[1]*prog)
            b = int(self.sky_color_top[2]*(1-prog) + self.sky_color_bot[2]*prog)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.map_width, y))
            
        pygame.draw.circle(surface, (255, 255, 200), (self.map_width//2, 150), 80)
        for r in range(80, 200, 10):
            alpha = 150 - r/1.5
            if alpha > 0:
                s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 200, 100, int(alpha)), (r, r), r)
                surface.blit(s, (self.map_width//2 - r, 150 - r))

    def update(self):
        self.anim_timer += 0.04
        self.mirage_timer += 0.01
        for p in self.dust_storm:
            p.update()

    def draw(self, screen, camera_x, camera_y):
        view_surf = pygame.Surface((WIDTH, HEIGHT))
        sky_canvas = pygame.Surface((self.map_width, self.map_height))
        self.draw_sky(sky_canvas)
        view_surf.blit(sky_canvas, (-camera_x * 0.15, -camera_y * 0.15))
        
        float_y = math.sin(self.anim_timer) * 15
        mirage_offset = math.sin(self.mirage_timer) * 3
        temp_canvas = self.static_canvas.copy()
        
        view_surf.blit(temp_canvas, (-camera_x + mirage_offset, -camera_y + int(float_y)))
        
        storm_surf = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        for p in self.dust_storm:
            p.draw(storm_surf)
        view_surf.blit(storm_surf, (-camera_x, -camera_y))
        
        screen.blit(view_surf, (0, 0))
        font = pygame.font.SysFont('trebuchetms', 30, bold=True)
        t_shadow = font.render(f"{self.name}", True, BLACK)
        t_main = font.render(f"{self.name}", True, (255, 200, 100))
        screen.blit(t_shadow, (22, 22))
        screen.blit(t_main, (20, 20))