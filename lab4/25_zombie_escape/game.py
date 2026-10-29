import pygame
import random
import math
import time

WIDTH, HEIGHT = 800, 560
FPS = 60
BG = (30,35,25)

# --- Tunables for the new features ---
PLAYER_MAX_HP = 3
INVINCIBLE_FRAMES = 90        # 1.5 s at 60 FPS
CLIP_SIZE = 12
RELOAD_MS = 2000              # 2 seconds
NUM_BARRELS = 4
BLAST_RADIUS = 110
EXPLOSION_FRAMES = 24         # how long the blast animation lasts


class Zombie:
    SPEED = 1.5
    HP = 3
    SIZE = 30
    COLOR = (60,140,60)

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        # Float position: Rect only stores ints, which would truncate slow speeds to 0
        self.x, self.y = float(x), float(y)
        self.color = self.COLOR
        self.hp = self.max_hp = self.HP
        self.wobble = random.uniform(0, 6.28)
        self.frame = 0

    def update(self, player_pos):
        px, py = player_pos
        cx, cy = self.rect.center
        dx, dy = px-cx, py-cy
        dist = (dx**2+dy**2)**0.5
        if dist:
            self.x += dx/dist*self.SPEED
            self.y += dy/dist*self.SPEED
            self.rect.topleft = (round(self.x), round(self.y))
        self.frame += 1

    def hit(self):
        self.hp -= 1
        return self.hp <= 0

    def draw(self, screen):
        wobble_y = int(math.sin(self.frame*0.2)*3)
        draw_rect = self.rect.move(0, wobble_y)
        pygame.draw.rect(screen, self.color, draw_rect, border_radius=5)
        eye_r = max(2, self.SIZE // 7)
        for ex in (draw_rect.x + self.SIZE*0.2, draw_rect.x + self.SIZE*0.6):
            pygame.draw.circle(screen, (200,40,40), (int(ex), draw_rect.y + self.SIZE//3), eye_r)
        # Small health bar once a zombie has taken damage
        if self.hp < self.max_hp:
            bar_w = self.rect.width
            pygame.draw.rect(screen, (90,20,20), (self.rect.x, self.rect.y-8, bar_w, 4))
            pygame.draw.rect(screen, (80,220,80),
                             (self.rect.x, self.rect.y-8, int(bar_w*self.hp/self.max_hp), 4))


class FastZombie(Zombie):
    SPEED = 2.8
    HP = 1
    SIZE = 20
    COLOR = (190,200,50)


class TankZombie(Zombie):
    SPEED = 0.8
    HP = 6
    SIZE = 44
    COLOR = (110,60,130)


def spawn_zombie(width, height, player_rect, margin=120):
    cls = random.choices([Zombie, FastZombie, TankZombie], weights=[60, 25, 15])[0]
    while True:
        x = random.randint(0, width-cls.SIZE)
        y = random.randint(0, height-cls.SIZE)
        rect = pygame.Rect(x, y, cls.SIZE, cls.SIZE)
        if not rect.colliderect(player_rect.inflate(margin, margin)):
            return cls(x, y)


class Barrel:
    W, H = 28, 34

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.W, self.H)

    def draw(self, screen):
        pygame.draw.rect(screen, (170,50,40), self.rect, border_radius=4)
        for off in (8, self.H-10):
            pygame.draw.line(screen, (60,20,20),
                             (self.rect.x, self.rect.y+off), (self.rect.right-1, self.rect.y+off), 3)
        pygame.draw.rect(screen, (240,200,60), self.rect, 2, border_radius=4)


def spawn_barrels(count, player_rect):
    barrels = []
    while len(barrels) < count:
        x = random.randint(20, WIDTH-Barrel.W-20)
        y = random.randint(60, HEIGHT-Barrel.H-20)
        b = Barrel(x, y)
        if b.rect.colliderect(player_rect.inflate(160, 160)):
            continue
        if any(b.rect.colliderect(o.rect.inflate(40, 40)) for o in barrels):
            continue
        barrels.append(b)
    return barrels


SPEED = 4

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (60,160,220)
        self.bullets = []
        self.shoot_cooldown = 0
        self.hp = PLAYER_MAX_HP
        self.invincible = 0            # frames of invincibility left
        self.ammo = CLIP_SIZE
        self.reloading = False
        self.reload_end = 0            # pygame ticks (ms) when reload finishes

    def move(self, keys, width, height):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = SPEED
        self.rect.x = max(0, min(width-self.rect.width, self.rect.x+dx))
        self.rect.y = max(0, min(height-self.rect.height, self.rect.y+dy))
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1

    def take_hit(self):
        """Lose 1 HP unless still invincible from a previous hit."""
        if self.invincible > 0:
            return
        self.hp -= 1
        self.invincible = INVINCIBLE_FRAMES

    def start_reload(self):
        if not self.reloading:
            self.reloading = True
            self.reload_end = pygame.time.get_ticks() + RELOAD_MS

    def update_reload(self):
        if self.reloading and pygame.time.get_ticks() >= self.reload_end:
            self.ammo = CLIP_SIZE
            self.reloading = False

    def reload_seconds_left(self):
        return max(0, self.reload_end - pygame.time.get_ticks()) / 1000

    def shoot(self, target_pos):
        if self.reloading: return
        if self.ammo <= 0:
            self.start_reload()
            return
        if self.shoot_cooldown > 0: return
        cx, cy = self.rect.center
        tx, ty = target_pos
        dx, dy = tx-cx, ty-cy
        dist = (dx**2+dy**2)**0.5
        if dist == 0: return
        vx, vy = dx/dist*10, dy/dist*10
        self.bullets.append([cx-4, cy-4, vx, vy])
        self.shoot_cooldown = 15
        self.ammo -= 1
        if self.ammo == 0:
            self.start_reload()

    def update_bullets(self, width, height):
        live = []
        for b in self.bullets:
            b[0] += b[2]; b[1] += b[3]
            if 0 <= b[0] <= width and 0 <= b[1] <= height:
                live.append(b)
        self.bullets = live

    def draw(self, screen):
        color = self.color
        # Flash white/blue while invincible so the window is visible
        if self.invincible > 0 and (self.invincible // 5) % 2 == 0:
            color = (230,240,255)
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        for b in self.bullets:
            pygame.draw.circle(screen, (255,220,60), (int(b[0]), int(b[1])), 5)


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zombie Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 24)
        self.hud_font = pygame.font.SysFont("monospace", 20)
        self.big_font = pygame.font.SysFont("monospace", 44, bold=True)
        self.reset()

    def reset(self):
        self.player = Player(WIDTH//2, HEIGHT//2)
        self.zombies = [spawn_zombie(WIDTH, HEIGHT, self.player.rect) for _ in range(4)]
        self.barrels = spawn_barrels(NUM_BARRELS, self.player.rect)
        self.explosions = []           # each: [x, y, frames_left]
        self.score = 0
        self.kill_points = 0           # bonus points from kills, kept separate from the timer
        self.wave = 1
        self.kills = 0
        self.kills_to_next = 8
        self.game_over = False
        self.start_time = time.time()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset()
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                self.player.shoot(event.pos)
        return True

    def explode_barrel(self, barrel, dead):
        """Blast every zombie within BLAST_RADIUS of the barrel's centre."""
        bx, by = barrel.rect.center
        self.explosions.append([bx, by, EXPLOSION_FRAMES])
        for z in self.zombies:
            zx, zy = z.rect.center
            if math.hypot(zx-bx, zy-by) <= BLAST_RADIUS:
                dead.append(z)

    def update(self):
        if self.game_over: return
        keys = pygame.key.get_pressed()
        self.player.move(keys, WIDTH, HEIGHT)
        self.player.update_bullets(WIDTH, HEIGHT)
        self.player.update_reload()
        self.score = int(time.time() - self.start_time) + self.kill_points

        for e in self.explosions:
            e[2] -= 1
        self.explosions = [e for e in self.explosions if e[2] > 0]

        for z in self.zombies:
            z.update(self.player.rect.center)
            if z.rect.colliderect(self.player.rect):
                self.player.take_hit()
        if self.player.hp <= 0:
            self.game_over = True

        dead = []

        # Bullets vs barrels
        for barrel in self.barrels[:]:
            for b in self.player.bullets[:]:
                if barrel.rect.collidepoint(int(b[0]), int(b[1])):
                    self.player.bullets.remove(b)
                    self.barrels.remove(barrel)
                    self.explode_barrel(barrel, dead)
                    break

        # Bullets vs zombies
        for z in self.zombies:
            for b in self.player.bullets[:]:
                bx, by = int(b[0]), int(b[1])
                if z.rect.collidepoint(bx, by):
                    if z.hit():
                        dead.append(z)
                    if b in self.player.bullets:
                        self.player.bullets.remove(b)

        for z in dead:
            if z in self.zombies:
                self.zombies.remove(z)
                self.kills += 1
                self.kill_points += 10
                if self.kills >= self.kills_to_next:
                    self.kills = 0
                    self.wave += 1
                    self.kills_to_next = 8 + self.wave * 2
                    for _ in range(self.wave + 3):
                        self.zombies.append(spawn_zombie(WIDTH, HEIGHT, self.player.rect))

    def draw_hud(self):
        pygame.draw.rect(self.screen, (15,20,15), pygame.Rect(0, 0, WIDTH, 40))
        left = self.hud_font.render(
            f"Wave {self.wave}  Score {self.score}  Kills {self.kills}/{self.kills_to_next}",
            True, (160,220,120))
        self.screen.blit(left, (8, 10))

        # HP: one box per hit point
        hp_label = self.hud_font.render("HP", True, (160,220,120))
        self.screen.blit(hp_label, (420, 10))
        for i in range(PLAYER_MAX_HP):
            color = (210,50,50) if i < self.player.hp else (60,40,40)
            pygame.draw.rect(self.screen, color, (456 + i*26, 10, 20, 20), border_radius=4)

        # Ammo / reload
        if self.player.reloading:
            txt = f"RELOAD {self.player.reload_seconds_left():.1f}s"
            color = (255,180,60)
        else:
            txt = f"AMMO {self.player.ammo}/{CLIP_SIZE}"
            color = (160,220,120)
        ammo = self.hud_font.render(txt, True, color)
        self.screen.blit(ammo, (WIDTH - ammo.get_width() - 12, 10))

    def draw(self):
        self.screen.fill(BG)
        for x in range(0, WIDTH, 60):
            pygame.draw.line(self.screen, (40,45,35), (x,0), (x,HEIGHT), 1)
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(self.screen, (40,45,35), (0,y), (WIDTH,y), 1)

        for barrel in self.barrels: barrel.draw(self.screen)
        for z in self.zombies: z.draw(self.screen)
        self.player.draw(self.screen)

        for x, y, left in self.explosions:
            progress = 1 - left / EXPLOSION_FRAMES
            r = int(BLAST_RADIUS * (0.3 + 0.7*progress))
            pygame.draw.circle(self.screen, (255,200,60), (x, y), int(r*0.6))
            pygame.draw.circle(self.screen, (255,120,30), (x, y), r, 6)

        self.draw_hud()

        if self.game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            self.screen.blit(ov, (0,0))
            m = self.big_font.render("DEVOURED!", True, (180,40,40))
            s = self.font.render(f"Wave {self.wave} | Score {self.score} | Press R", True, (200,200,200))
            self.screen.blit(m, (WIDTH//2-m.get_width()//2, HEIGHT//2-40))
            self.screen.blit(s, (WIDTH//2-s.get_width()//2, HEIGHT//2+20))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    engine = GameEngine()
    engine.run()