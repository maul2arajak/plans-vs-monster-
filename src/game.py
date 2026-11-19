import random
import pygame
from .settings import *
from .support import load_image, load_frames, draw_text
from .tilemap import TiledMapRenderer
from .entities import Monster, PlantFactory, ShooterPlant
from .ui import UI
from .cutscene import CutscenePlayer


class Game:
    def __init__(self):
        pygame.init()
        self.audio_enabled = False
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except pygame.error as exc:
            print(f'Audio nonaktif: {exc}')
        pygame.display.set_caption('Coffee vs Monster - Haunted Lawn')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        font_path = ASSET_DIR / 'fonts/m6x11.ttf'
        if font_path.exists():
            self.font = pygame.font.Font(str(font_path), 24)
            self.font_small = pygame.font.Font(str(font_path), 19)
            self.font_tiny = pygame.font.Font(str(font_path), 16)
            self.font_big = pygame.font.Font(str(font_path), 46)
        else:
            self.font = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 22)
            self.font_tiny = pygame.font.Font(None, 18)
            self.font_big = pygame.font.Font(None, 46)

        self.map = TiledMapRenderer()
        self.load_assets()
        self.cutscene_player = CutscenePlayer(self.screen, self.clock, self.audio_enabled, self.font_small)
        self.reset()

    def load_assets(self):
        self.assets = {
            'coffee': load_image(ASSET_DIR / 'plants/coffee_plant.png', PLANT_SCALES['coffee']),
            'shooter': load_image(ASSET_DIR / 'plants/shooter_plant.png', PLANT_SCALES['shooter']),
            'bomb': load_image(ASSET_DIR / 'plants/bomb_plant.png', PLANT_SCALES['bomb']),
            'shield': load_image(ASSET_DIR / 'plants/shield_plant.png', PLANT_SCALES['shield']),
            'coffee_bean': load_image(ASSET_DIR / 'plants/coffee_bean.png', PLANT_SCALES['coffee_bean']),
            'projectile': load_image(ASSET_DIR / 'plants/projectile.png', PLANT_SCALES['projectile']),
            'shovel': load_image(ASSET_DIR / 'ui/shovel.png', (46, 46)),
            'heart': load_image(ASSET_DIR / 'ui/heart.png', (26, 24)),
        }
        self.card_assets = {}
        for ptype in PLANT_ORDER:
            path = ASSET_DIR / f'ui/cards/{ptype}.png'
            if path.exists():
                self.card_assets[ptype] = load_image(path)

        self.coffee_frames = load_frames(ASSET_DIR / 'plants/coffee_anim', scale=PLANT_SCALES['coffee'])
        if not self.coffee_frames:
            self.coffee_frames = [self.assets['coffee']]

        self.shooter_frames = load_frames(ASSET_DIR / 'plants/shooter_anim', scale=PLANT_SCALES['shooter'])
        if not self.shooter_frames:
            self.shooter_frames = [self.assets['shooter']]
        self.monster_walk_frames = load_frames(ASSET_DIR / 'monster/walk_left', scale=MONSTER_FRAME_SCALE)
        self.monster_attack_frames = load_frames(ASSET_DIR / 'monster/attack_left', scale=MONSTER_FRAME_SCALE)
        self.explosion_frames = load_frames(ASSET_DIR / 'effects/explosion_anim', scale=(92, 92))
        self.sounds = self.load_sounds()

    def load_sounds(self):
        sounds = {}
        if not self.audio_enabled:
            return sounds

        sound_paths = {
            'monster_howl': MONSTER_HOWL_SOUND,
            'monster_attack': MONSTER_ATTACK_SOUND,
            'shooter_shoot': SHOOTER_SHOOT_SOUND,
            'projectile_hit': PROJECTILE_HIT_SOUND,
            'bomb_explosion': BOMB_EXPLOSION_SOUND,
        }
        volumes = {
            'monster_howl': 0.85,
            'monster_attack': 0.78,
            'shooter_shoot': 0.55,
            'projectile_hit': 0.62,
            'bomb_explosion': 0.90,
        }

        for name, path in sound_paths.items():
            try:
                if path.exists():
                    sound = pygame.mixer.Sound(str(path))
                    sound.set_volume(volumes.get(name, 0.7))
                    sounds[name] = sound
            except pygame.error as exc:
                print(f'SFX gagal dimuat {path.name}: {exc}')
        return sounds

    def play_sound(self, name):
        if not self.audio_enabled:
            return
        sound = getattr(self, 'sounds', {}).get(name)
        if sound:
            try:
                sound.play()
            except pygame.error:
                pass

    def start_music(self):
        if not self.audio_enabled:
            return
        try:
            pygame.mixer.music.load(str(GAME_MUSIC))
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1)
            self.music_playing = True
        except pygame.error as exc:
            print(f'Musik gagal diputar: {exc}')
            self.music_playing = False

    def stop_music(self):
        if not self.audio_enabled:
            return
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
        except pygame.error:
            pass

    def play_cutscene(self, video_path, audio_path):
        self.stop_music()
        if self.audio_enabled:
            try:
                pygame.mixer.stop()
            except pygame.error:
                pass
        return self.cutscene_player.play(video_path, audio_path)

    def finish_game(self, state):
        if self.state != 'play':
            return
        self.state = state
        self.stop_music()
        if state == 'win':
            self.play_cutscene(WIN_VIDEO, WIN_VIDEO_AUDIO)
        else:
            self.play_cutscene(LOSE_VIDEO, LOSE_VIDEO_AUDIO)
        # Setelah video menang atau kalah selesai maupun di-skip, program langsung keluar.
        self.running = False

    def reset(self):
        self.all_sprites = pygame.sprite.Group()
        self.plants = pygame.sprite.Group()
        self.beans = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.selected_index = 0
        self.plant_counts = {k: 0 for k in PLANT_LIMITS}
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.coffee_stock = 0
        self.elapsed_ms = 0
        self.finish_clock_hold_ms = 0
        self.spawn_timer = MONSTER_INITIAL_TIMER_MS
        self.score = 0
        self.lives = 3
        self.state = 'play'
        self.music_playing = False
        self.flashes = []
        self.dragging_bean = None
        self.dragging_plant_type = None
        self.dragging_plant_image = None
        self.dragging_plant_slot = None
        self.shovel_mode = False
        self.ui = UI(self)

    def cell_center(self, row, col):
        return (GRID_X + col * CELL_W + CELL_W // 2, GRID_Y + row * CELL_H + CELL_H // 2)

    def cell_midbottom(self, row, col):
        x, y = self.cell_center(row, col)
        return (x, y + CELL_H // 2 - 4)

    def grid_from_pos(self, pos):
        x, y = pos
        if GRID_X <= x < GRID_X + GRID_W and GRID_Y <= y < GRID_Y + GRID_H:
            col = int((x - GRID_X) // CELL_W)
            row = int((y - GRID_Y) // CELL_H)
            return row, col
        return None

    @property
    def selected_type(self):
        return PLANT_ORDER[self.selected_index]

    def add_flash(self, center, color):
        self.flashes.append([center, 0, color])

    def remove_plant(self, plant, free_limit=True):
        if 0 <= plant.row < GRID_ROWS and 0 <= plant.col < GRID_COLS:
            if self.grid[plant.row][plant.col] is plant:
                self.grid[plant.row][plant.col] = None

        # free_limit=True hanya untuk tanaman yang dihapus manual dengan skop.
        # Kalau tanaman kalah dimakan monster atau bom sudah dipakai/meledak,
        # jatah kartu tetap terpakai sehingga tidak bisa ditambah lagi melebihi batas.
        if free_limit:
            self.plant_counts[plant.plant_type] = max(0, self.plant_counts[plant.plant_type] - 1)
        plant.kill()

    def can_place(self, row, col, ptype=None):
        ptype = ptype or self.selected_type
        if not (0 <= row < GRID_ROWS and 0 <= col < GRID_COLS):
            return False
        if self.grid[row][col] is not None:
            return False
        if self.plant_counts[ptype] >= PLANT_LIMITS[ptype]:
            return False
        return True

    def try_place(self, row, col, ptype=None):
        ptype = ptype or self.selected_type
        if not self.can_place(row, col, ptype):
            return False
        plant = PlantFactory.create(self, ptype, row, col)
        self.grid[row][col] = plant
        self.plant_counts[ptype] += 1
        return True

    def get_bean_at_pos(self, pos):
        for bean in reversed(self.beans.sprites()):
            if bean.rect.collidepoint(pos):
                return bean
        return None

    def get_shooter_at_pos(self, pos):
        for plant in self.plants:
            if isinstance(plant, ShooterPlant) and plant.rect.collidepoint(pos):
                return plant
        return None

    def start_plant_drag(self, slot_index):
        self.selected_index = slot_index
        ptype = PLANT_ORDER[slot_index]
        if self.plant_counts[ptype] >= PLANT_LIMITS[ptype]:
            return
        self.dragging_plant_type = ptype
        self.dragging_plant_image = self.assets[ptype].copy()
        self.dragging_plant_image.set_alpha(190)
        self.dragging_plant_slot = slot_index
        pygame.mouse.set_visible(True)

    def cancel_plant_drag(self):
        self.dragging_plant_type = None
        self.dragging_plant_image = None
        self.dragging_plant_slot = None
        pygame.mouse.set_visible(True)

    @property
    def difficulty_label(self):
        """Teks tingkat kesulitan berdasarkan durasi nyata permainan.

        Pembagian fase dibuat eksplisit agar pemain merasakan 2 menit mudah,
        2 menit sedang, lalu 1 menit sulit sebelum jam UI mencapai 06.00 pagi.
        """
        if self.elapsed_ms < DIFFICULTY_EASY_END_MS:
            return 'Mudah'
        if self.elapsed_ms < DIFFICULTY_MEDIUM_END_MS:
            return 'Sedang'
        return 'Sulit'

    def monster_spawn_profile(self):
        """Hitung interval dan jumlah monster sesuai progres permainan.

        Fase mudah berlangsung 2 menit pertama. Fase sedang berlangsung
        2 menit berikutnya. Menit terakhir menjadi fase sulit. Interval spawn
        tetap berubah secara bertahap agar perpindahan tingkat tidak terasa
        terlalu mendadak.
        """
        progress = min(1.0, self.elapsed_ms / GAME_DURATION_MS)
        interval = max(
            MONSTER_MIN_SPAWN_MS,
            int(MONSTER_SPAWN_BASE_MS - progress * MONSTER_SPAWN_REDUCTION_MS),
        )

        batch_size = 1
        if self.elapsed_ms >= DIFFICULTY_EASY_END_MS and random.random() < (0.22 + progress * 0.28):
            batch_size += 1
        if self.elapsed_ms >= DIFFICULTY_MEDIUM_END_MS and random.random() < (0.10 + progress * 0.20):
            batch_size += 1
        return interval, min(batch_size, GRID_ROWS)

    def spawn_monsters(self, dt):
        if self.elapsed_ms < MONSTER_FIRST_SPAWN_DELAY_MS:
            return

        self.spawn_timer -= dt
        if self.spawn_timer > 0:
            return

        next_spawn, batch_size = self.monster_spawn_profile()
        jitter = max(250, int(next_spawn * 0.10))
        self.spawn_timer = max(1_200, next_spawn + random.randint(-jitter, jitter))

        # Monster dalam satu gelombang ditempatkan di lane berbeda agar pola
        # serangan lebih ramai tetapi tetap dapat dibaca oleh pemain.
        lanes = random.sample(range(GRID_ROWS), k=batch_size)
        for row in lanes:
            Monster(self, row)

    def handle_mouse_down(self, pos):
        if self.state != 'play':
            return

        # alat skop / shovel untuk menghapus tanaman
        if self.ui.shovel_rect().collidepoint(pos):
            self.shovel_mode = not self.shovel_mode
            return

        if self.shovel_mode:
            cell = self.grid_from_pos(pos)
            if cell:
                row, col = cell
                plant = self.grid[row][col]
                if plant:
                    self.remove_plant(plant, free_limit=True)
                    self.shovel_mode = False
            return

        # 1) kartu tanaman: seperti seed packet PvZ, klik/tahan lalu lepas di rumput
        slot = self.ui.slot_at_pos(pos)
        if slot is not None:
            self.start_plant_drag(slot)
            return

        # 2) biji kopi: tarik ke penembak
        bean = self.get_bean_at_pos(pos)
        if bean:
            self.dragging_bean = bean
            bean.start_drag(pos)
            return

    def handle_mouse_up(self, pos):
        if self.dragging_plant_type:
            cell = self.grid_from_pos(pos)
            if cell:
                row, col = cell
                self.try_place(row, col, self.dragging_plant_type)
            self.cancel_plant_drag()
            return

        if self.dragging_bean:
            shooter = self.get_shooter_at_pos(pos)
            bean = self.dragging_bean
            self.dragging_bean = None
            if shooter:
                bean.drop_on_shooter(shooter)
            else:
                bean.cancel_drag()

    def events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
                if e.key == pygame.K_a:
                    self.selected_index = (self.selected_index - 1) % len(PLANT_ORDER)
                elif e.key == pygame.K_d:
                    self.selected_index = (self.selected_index + 1) % len(PLANT_ORDER)
                elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.selected_index = e.key - pygame.K_1
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.handle_mouse_down(e.pos)
            elif e.type == pygame.MOUSEMOTION:
                if self.dragging_bean:
                    self.dragging_bean.drag_to(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self.handle_mouse_up(e.pos)

    def update(self, dt):
        if self.state != 'play':
            return
        if self.lives <= 0:
            self.finish_game('lose')
            return

        self.elapsed_ms = min(GAME_DURATION_MS, self.elapsed_ms + dt)


        if self.elapsed_ms >= GAME_DURATION_MS:
            self.finish_clock_hold_ms += dt
            if self.finish_clock_hold_ms >= FINISH_CLOCK_HOLD_MS:
                self.finish_game('win')
            return

        self.spawn_monsters(dt)
        self.all_sprites.update(dt)
        for flash in self.flashes:
            flash[1] += dt
        self.flashes = [f for f in self.flashes if f[1] < 360]


    def draw_grid_guides(self):
        guide = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
       
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * CELL_H, CELL_W, CELL_H)
                pygame.draw.rect(guide, (0, 0, 0, 95), rect, 1)
        
        for row in range(GRID_ROWS + 1):
            y = GRID_Y + row * CELL_H
            pygame.draw.line(guide, (0, 0, 0, 70), (GRID_X, y), (SCREEN_WIDTH - 70, y), 1)
        self.screen.blit(guide, (0, 0))

    def draw_flashes(self):
        for center, age, color in self.flashes:
            radius = int(16 + age * 0.22)
            alpha = max(0, 155 - int(age * 0.38))
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), radius)
            self.screen.blit(surf, (center[0] - radius, center[1] - radius))

    def draw_hover_and_ghost(self):
        if self.state != 'play':
            return
        pos = pygame.mouse.get_pos()
        cell = self.grid_from_pos(pos)
        if not cell:
            if self.dragging_plant_type and self.dragging_plant_image:
                img = self.dragging_plant_image
                self.screen.blit(img, img.get_rect(center=pos))
            if self.shovel_mode:
                self.screen.blit(self.assets['shovel'], self.assets['shovel'].get_rect(center=pos))
            return

        row, col = cell
        rect = pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * CELL_H, CELL_W, CELL_H)

        if self.shovel_mode:
            color = (255, 80, 80) if self.grid[row][col] else (130, 80, 80)
            pygame.draw.rect(self.screen, color, rect, 3, border_radius=4)
            self.screen.blit(self.assets['shovel'], self.assets['shovel'].get_rect(center=(pos[0] + 18, pos[1] - 18)))
            return

        ok = self.can_place(row, col, self.dragging_plant_type or self.selected_type)
        color = (255, 240, 125) if ok else (225, 75, 75)
        pygame.draw.rect(self.screen, color, rect, 2, border_radius=4)
        if self.dragging_plant_type and self.dragging_plant_image:
            img = self.dragging_plant_image
            ghost = img.copy()
            ghost.set_alpha(145 if ok else 90)
            self.screen.blit(ghost, ghost.get_rect(midbottom=self.cell_midbottom(row, col)))

    def draw(self):
        self.map.draw(self.screen)
        self.draw_grid_guides()

      
        dragging_bean = self.dragging_bean
        for sprite in sorted(self.all_sprites, key=lambda s: s.rect.bottom):
            if dragging_bean and sprite is dragging_bean:
                continue
            self.screen.blit(sprite.image, sprite.rect)
        if dragging_bean:
            self.screen.blit(dragging_bean.image, dragging_bean.rect)

        self.draw_hover_and_ghost()
        self.draw_flashes()
        for p in self.plants:
            p.draw_overlay(self.screen)
        for m in self.monsters:
            m.draw_overlay(self.screen)
        self.ui.draw(self.screen)
        pygame.display.flip()

    def run(self):
       
        self.stop_music()
        self.running = self.cutscene_player.play(INTRO_VIDEO, INTRO_VIDEO_AUDIO, required=True)
        if self.running:
            self.start_music()
        while self.running:
            dt = self.clock.tick(FPS)
            self.events()
            self.update(dt)
            if not self.running:
                break
            self.draw()
        self.stop_music()
        pygame.quit()
