#!/usr/bin/env python3
"""
Realistic Mario - Level 1-1 inspired prototype
Uses the MFGG Realistic Mario sprite sheet.
Mechanics:
- Headbonk on bricks/blocks = death (realistic trauma)
- Water sections drain oxygen and cause drowning death
- Simple platformer controls

This is an ORIGINAL short level inspired by the spirit of SMB 1-1,
NOT a pixel-perfect copy of Nintendo's copyrighted level data.
"""

import pygame
import sys
import os

# --- Config ---
SCREEN_W, SCREEN_H = 800, 480
FPS = 60
GRAVITY = 0.6
JUMP_STRENGTH = -12
MOVE_SPEED = 4
TILE = 32

# Colors
SKY = (135, 206, 235)
GROUND = (34, 139, 34)
DIRT = (139, 69, 19)
BRICK = (180, 100, 50)
PIPE = (0, 150, 0)
WATER = (30, 100, 200)
CLOUD = (255, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
HUD_BG = (0, 0, 0, 160)

# Paths
SHEET_PATH = os.path.join(os.path.dirname(__file__), "assets", "realistic_mario_sheet.png")
SHEET_URL = "https://mfgg.net/index.php?act=resdb&param=03&c=1&id=34896"

def ensure_sheet():
    """Download the Realistic Mario sheet from MFGG if not present."""
    os.makedirs(os.path.dirname(SHEET_PATH), exist_ok=True)
    if not os.path.exists(SHEET_PATH):
        print("Downloading Realistic Mario sprite sheet from MFGG...")
        try:
            import urllib.request
            urllib.request.urlretrieve(SHEET_URL, SHEET_PATH)
            print("Done.")
        except Exception as e:
            print("Could not download sheet:", e)
            print("Place realistic_mario_sheet.png in the assets/ folder manually.")
            sys.exit(1)

class Player:
    def __init__(self, x, y, sheet):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.w = 28
        self.h = 40
        self.on_ground = False
        self.facing = 1  # 1 right, -1 left
        self.alive = True
        self.death_timer = 0
        self.death_reason = ""
        self.oxygen = 100.0
        self.in_water = False
        self.sheet = sheet
        # Try to grab a rough Mario-ish region from the sheet (manual-ish crop)
        # Sheet is 800x600; we'll just use a centralish upright pose as placeholder
        try:
            # Rough standing pose area (adjust if needed after visual check)
            self.frame = sheet.subsurface(pygame.Rect(50, 20, 60, 80)).copy()
            self.frame = pygame.transform.scale(self.frame, (self.w, self.h))
            self.dead_frame = sheet.subsurface(pygame.Rect(200, 100, 60, 80)).copy()
            self.dead_frame = pygame.transform.scale(self.dead_frame, (self.w, self.h))
        except Exception:
            self.frame = pygame.Surface((self.w, self.h))
            self.frame.fill(RED)
            self.dead_frame = self.frame.copy()

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, keys, platforms, water_rects):
        if not self.alive:
            self.death_timer += 1
            self.vy += GRAVITY * 0.5
            self.y += self.vy
            return

        # Horizontal
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -MOVE_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = MOVE_SPEED
            self.facing = 1

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground and not self.in_water:
            self.vy = JUMP_STRENGTH
            self.on_ground = False

        # Water physics
        self.in_water = any(self.rect().colliderect(w) for w in water_rects)
        if self.in_water:
            self.vy += GRAVITY * 0.3
            self.vy = max(min(self.vy, 3), -4)
            self.oxygen -= 0.4
            if self.oxygen <= 0:
                self.die("drowned")
        else:
            self.vy += GRAVITY
            self.oxygen = min(100.0, self.oxygen + 0.8)

        # Apply velocity
        self.x += self.vx
        self.y += self.vy

        # Collisions
        self.on_ground = False
        p_rect = self.rect()

        for plat in platforms:
            if p_rect.colliderect(plat.rect):
                # Headbonk detection: coming from below into a solid brick/block
                if self.vy < 0 and p_rect.top < plat.rect.bottom and p_rect.centery > plat.rect.centery:
                    if plat.is_brick:
                        self.die("head trauma from brick")
                        return
                    # Regular solid
                    self.y = plat.rect.bottom
                    self.vy = 0
                # Landing on top
                elif self.vy >= 0 and p_rect.bottom > plat.rect.top and p_rect.centery < plat.rect.centery:
                    self.y = plat.rect.top - self.h
                    self.vy = 0
                    self.on_ground = True
                # Side collisions
                elif self.vx > 0:
                    self.x = plat.rect.left - self.w
                elif self.vx < 0:
                    self.x = plat.rect.right

        # Screen bounds / pit death
        if self.y > SCREEN_H + 50:
            self.die("fell into the abyss")
        if self.x < 0:
            self.x = 0
        if self.x > 3200:  # level length
            self.x = 3200

    def die(self, reason):
        self.alive = False
        self.death_reason = reason
        self.vy = -6  # little bounce of death
        self.death_timer = 0

    def draw(self, surf, camera_x):
        img = self.dead_frame if not self.alive else self.frame
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        surf.blit(img, (int(self.x - camera_x), int(self.y)))


class Platform:
    def __init__(self, x, y, w, h, is_brick=False, color=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.is_brick = is_brick
        self.color = color or (BRICK if is_brick else GROUND)

    def draw(self, surf, camera_x):
        r = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surf, self.color, r)
        if self.is_brick:
            # Simple brick lines
            for i in range(0, self.rect.w, 16):
                pygame.draw.line(surf, (120, 60, 30), (r.x + i, r.y), (r.x + i, r.bottom), 1)
            pygame.draw.line(surf, (120, 60, 30), (r.x, r.y + self.rect.h // 2), (r.right, r.y + self.rect.h // 2), 1)


def build_level():
    platforms = []
    water = []

    # Ground sections (inspired by 1-1 structure, original layout)
    # Main ground
    platforms.append(Platform(0, 400, 600, 80, color=GROUND))
    platforms.append(Platform(700, 400, 400, 80, color=GROUND))
    platforms.append(Platform(1200, 400, 500, 80, color=GROUND))
    platforms.append(Platform(1800, 400, 800, 80, color=GROUND))
    platforms.append(Platform(2700, 400, 600, 80, color=GROUND))

    # Floating bricks / question-block style (deadly on headbonk)
    platforms.append(Platform(250, 280, 32, 32, is_brick=True))
    platforms.append(Platform(300, 280, 32, 32, is_brick=True))
    platforms.append(Platform(350, 280, 32, 32, is_brick=True))
    platforms.append(Platform(900, 250, 32, 32, is_brick=True))
    platforms.append(Platform(950, 250, 96, 32, is_brick=True))
    platforms.append(Platform(1400, 220, 32, 32, is_brick=True))
    platforms.append(Platform(1450, 220, 32, 32, is_brick=True))
    platforms.append(Platform(1500, 220, 32, 32, is_brick=True))
    platforms.append(Platform(2000, 280, 128, 32, is_brick=True))

    # Pipes (solid, not head-deadly)
    platforms.append(Platform(500, 336, 64, 64, color=PIPE))
    platforms.append(Platform(1100, 304, 64, 96, color=PIPE))
    platforms.append(Platform(1600, 336, 64, 64, color=PIPE))
    platforms.append(Platform(2300, 272, 64, 128, color=PIPE))

    # Stairs-ish toward end
    for i in range(5):
        platforms.append(Platform(2500 + i * 32, 400 - (i + 1) * 32, 32 * (5 - i), 32, color=DIRT))

    # Water pit section
    water.append(pygame.Rect(600, 420, 100, 80))
    platforms.append(Platform(600, 460, 100, 40, color=DIRT))  # bottom of pit

    # Another water area later
    water.append(pygame.Rect(1700, 420, 100, 80))
    platforms.append(Platform(1700, 460, 100, 40, color=DIRT))

    return platforms, water


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Realistic Mario – Level 1-1 Inspired (Head Trauma Edition)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)
    big_font = pygame.font.SysFont("Arial", 36, bold=True)

    ensure_sheet()
    # Load sheet
    try:
        sheet = pygame.image.load(SHEET_PATH).convert_alpha()
    except Exception as e:
        print("Could not load sprite sheet:", e)
        sheet = pygame.Surface((100, 100))
        sheet.fill(RED)

    platforms, water_rects = build_level()
    player = Player(80, 300, sheet)
    camera_x = 0.0
    goal_x = 3000

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not player.alive:
                    # Restart
                    player = Player(80, 300, sheet)
                    camera_x = 0.0
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        player.update(keys, platforms, water_rects)

        # Camera
        target_cam = player.x - SCREEN_W // 3
        camera_x += (target_cam - camera_x) * 0.1
        camera_x = max(0, min(camera_x, 3200 - SCREEN_W))

        # Draw
        screen.fill(SKY)

        # Simple clouds
        for cx in range(0, 3500, 300):
            pygame.draw.ellipse(screen, CLOUD, (cx - camera_x, 60, 80, 30))
            pygame.draw.ellipse(screen, CLOUD, (cx + 30 - camera_x, 50, 60, 25))

        # Water
        for w in water_rects:
            r = w.move(-camera_x, 0)
            pygame.draw.rect(screen, WATER, r)
            # Waves
            for i in range(0, w.w, 20):
                pygame.draw.arc(screen, (100, 180, 255), (r.x + i, r.y - 5, 20, 10), 0, 3.14, 2)

        # Platforms
        for p in platforms:
            p.draw(screen, camera_x)

        # Goal flag-ish
        gx = goal_x - camera_x
        if 0 < gx < SCREEN_W:
            pygame.draw.rect(screen, (200, 200, 200), (gx, 200, 8, 200))
            pygame.draw.polygon(screen, RED, [(gx + 8, 200), (gx + 50, 220), (gx + 8, 240)])

        # Player
        player.draw(screen, camera_x)

        # HUD
        hud = pygame.Surface((SCREEN_W, 40), pygame.SRCALPHA)
        hud.fill(HUD_BG)
        screen.blit(hud, (0, 0))
        screen.blit(font.render("Realistic Mario – 1-1 Inspired", True, WHITE), (10, 10))
        screen.blit(font.render(f"O2: {int(player.oxygen)}%", True, WHITE if player.oxygen > 30 else RED), (300, 10))
        screen.blit(font.render("Arrows/WASD + Space  |  R = restart after death", True, WHITE), (450, 10))

        # Death overlay
        if not player.alive:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            msg = big_font.render("YOU DIED", True, RED)
            reason = font.render(f"Cause: {player.death_reason}", True, WHITE)
            tip = font.render("Press R to try again", True, WHITE)
            screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, 180))
            screen.blit(reason, (SCREEN_W // 2 - reason.get_width() // 2, 230))
            screen.blit(tip, (SCREEN_W // 2 - tip.get_width() // 2, 270))

        # Win check
        if player.alive and player.x > goal_x:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 80, 0, 180))
            screen.blit(overlay, (0, 0))
            msg = big_font.render("LEVEL CLEAR!", True, (100, 255, 100))
            tip = font.render("You survived the realism. Press ESC to quit.", True, WHITE)
            screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, 200))
            screen.blit(tip, (SCREEN_W // 2 - tip.get_width() // 2, 250))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
