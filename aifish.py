import tkinter as tk
import random
import time
import math
import pygame  

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FISH_WIDTH = 60
FISH_HEIGHT = 30
GAME_DURATION = 10  

FISH_COLORS = ["orange", "blue", "green", "purple", "yellow", "pink", "red", "black"]

class FishClickGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Catch the Fish!")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#66ccff")
        self.canvas.pack()

        self.wave_offset = 0
        self.wave_layers = []
        self.bubbles = []
        self.plants = []
        self.plant_sway_angle = 0
        self.fishes = []
        self.target_fish = None
        self.win = False
        self.game_over = False
        self.crab = None
        self.crab_direction = 1
        self.net = None

        self.draw_ocean_background()
        self.draw_sand_decor()
        self.draw_rocks()
        self.draw_plants()
        self.draw_crab()
        self.animate_crab()
        self.animate_waves()
        self.animate_plants()
        self.animate_bubbles()
        self.create_fishes()
        self.choose_target_fish()
        self.start_time = time.time()
        self.canvas.tag_bind("fish", "<Button-1>", self.on_fish_click)
        self.update_game()

        # Initialize pygame mixer to play sound/music
        pygame.mixer.init()

    def draw_ocean_background(self):
        self.canvas.create_rectangle(0, WINDOW_HEIGHT - 60, WINDOW_WIDTH, WINDOW_HEIGHT,
                                     fill="#d2b48c", outline="", tags="sand")
        for i in range(3):
            wave = self.canvas.create_line(0, 0, 0, 0, fill=["#0099cc", "#0077aa", "#005577"][i],
                                           width=2 + i, smooth=1, tags=f"wave_{i}")
            self.wave_layers.append((wave, 0.5 + i * 0.5))

    def draw_sand_decor(self):
        for _ in range(10):
            x = random.randint(20, WINDOW_WIDTH - 20)
            y = random.randint(WINDOW_HEIGHT - 55, WINDOW_HEIGHT - 10)
            self.canvas.create_arc(x, y, x+20, y+12, start=0, extent=180, fill="#fff5ee",
                                   outline="#d2b48c", style=tk.PIESLICE)

    def draw_crab(self):
        x = 100
        y = WINDOW_HEIGHT - 50
        body = self.canvas.create_oval(x, y, x+40, y+25, fill="maroon", outline="darkred", tags="crab")
        eyes = [
            self.canvas.create_oval(x+8, y-8, x+14, y-2, fill="white", tags="crab"),
            self.canvas.create_oval(x+26, y-8, x+32, y-2, fill="white", tags="crab"),
            self.canvas.create_oval(x+10, y-6, x+12, y-4, fill="black", tags="crab"),
            self.canvas.create_oval(x+28, y-6, x+30, y-4, fill="black", tags="crab")
        ]
        claws = [
            self.canvas.create_oval(x-10, y+5, x, y+15, fill="red", tags="crab"),
            self.canvas.create_oval(x+40, y+5, x+50, y+15, fill="red", tags="crab")
        ]
        legs = []
        for dx in [2, 8, 14, 26, 32, 38]:
            legs.append(self.canvas.create_line(x+dx, y+25, x+dx, y+35, fill="black", tags="crab"))
        self.crab = "crab"

    def animate_crab(self):
        if not self.game_over:
            dx = 2 * self.crab_direction
            crab_coords = self.canvas.bbox(self.crab)
            if crab_coords:
                x1, _, x2, _ = crab_coords
                if x2 >= WINDOW_WIDTH or x1 <= 0:
                    self.crab_direction *= -1
            self.canvas.move(self.crab, dx, 0)
        self.after(50, self.animate_crab)

    def animate_waves(self):
        self.wave_offset += 0.2
        for i, (wave, speed) in enumerate(self.wave_layers):
            points = []
            for x in range(0, WINDOW_WIDTH + 20, 20):
                y = 80 + i * 25 + 8 * math.sin((x * 0.05) + (self.wave_offset * speed))
                points.extend([x, y])
            self.canvas.coords(wave, *points)
        self.after(50, self.animate_waves)

    def draw_rocks(self):
        for _ in range(15):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(WINDOW_HEIGHT - 50, WINDOW_HEIGHT - 20)
            size = random.randint(20, 50)
            color = random.choice(["#666666", "#777777", "#888888"])
            self.canvas.create_oval(x, y, x + size, y + size // 2,
                                    fill=color, outline="#444444", tags="rock")

    def draw_plants(self):
        for x in range(50, WINDOW_WIDTH, 60):
            base_y = WINDOW_HEIGHT - 20
            plant = self.canvas.create_line(x, base_y, x, base_y - 60,
                                            fill="sea green", width=3, smooth=True, tags="plant")
            self.plants.append((plant, x, base_y))

    def animate_plants(self):
        self.plant_sway_angle += 0.15
        for plant, base_x, base_y in self.plants:
            sway = 12 * math.sin(self.plant_sway_angle + base_x * 0.01)
            mid_x = base_x + sway
            self.canvas.coords(plant, base_x, base_y, mid_x, base_y - 30, base_x, base_y - 60)
        self.after(80, self.animate_plants)

    def animate_bubbles(self):
        if random.random() < 0.3:
            x = random.randint(50, WINDOW_WIDTH - 50)
            size = random.randint(5, 12)
            bubble = self.canvas.create_oval(x, WINDOW_HEIGHT - 30,
                                             x + size, WINDOW_HEIGHT - 30 + size,
                                             outline="white", width=1, tags="bubble")
            self.bubbles.append((bubble, random.uniform(1, 3)))

        for bubble, speed in self.bubbles[:]:
            self.canvas.move(bubble, 0, -speed)
            if self.canvas.bbox(bubble)[1] < 0:
                self.canvas.delete(bubble)
                self.bubbles.remove((bubble, speed))

        self.after(50, self.animate_bubbles)

    def create_fishes(self):
        for color in FISH_COLORS:
            x = random.randint(100, WINDOW_WIDTH - FISH_WIDTH - 100)
            y = random.randint(150, WINDOW_HEIGHT - FISH_HEIGHT - 120)
            fish_id = self.draw_fish(x, y, color)
            self.fishes.append((fish_id, color))

    def draw_fish(self, x, y, color):
        fish_tag = f"fish_{color}"
        self.canvas.create_oval(x, y, x + FISH_WIDTH, y + FISH_HEIGHT,
                                fill=color, outline="darkred", tags=("fish", fish_tag))
        self.canvas.create_polygon(x, y + FISH_HEIGHT // 2,
                                   x - 20, y,
                                   x - 20, y + FISH_HEIGHT,
                                   fill="red", outline="darkred", tags=("fish", fish_tag))
        self.canvas.create_polygon(x + 20, y,
                                   x + 30, y - 15,
                                   x + 40, y,
                                   fill="darkorange", outline="black", tags=("fish", fish_tag))
        self.canvas.create_oval(x + FISH_WIDTH - 15, y + 5,
                                x + FISH_WIDTH - 5, y + 15,
                                fill="white", tags=("fish", fish_tag))
        self.canvas.create_oval(x + FISH_WIDTH - 10, y + 8,
                                x + FISH_WIDTH - 7, y + 12,
                                fill="black", tags=("fish", fish_tag))
        return fish_tag

    def choose_target_fish(self):
        self.target_fish = random.choice(self.fishes)
        _, color = self.target_fish
        self.canvas.create_text(WINDOW_WIDTH // 2, 30,
                                text=f"Find the {color} fish!", font=("Arial", 20, "bold"),
                                fill="white", tags="target_label")

    def on_fish_click(self, event):
        if self.game_over:
            return

        clicked_items = self.canvas.find_withtag("current")
        tags = self.canvas.gettags(clicked_items[0])
        if self.target_fish[0] in tags:
            self.win = True
            self.play_win_song()  # Play win song when the fish is caught
            self.show_net_animation()
        else:
            self.win = False
        self.end_game()

    def show_net_animation(self):
        # Show fishing net animation when the fish is clicked
        fish_coords = self.canvas.bbox(self.target_fish[0])
        if fish_coords:
            x1, y1, x2, y2 = fish_coords
            net_width = x2 - x1 + 40
            net_height = y2 - y1 + 40
            self.net = self.canvas.create_rectangle(x1 - 20, y1 - 20, x2 + 20, y2 + 20,
                                                    outline="darkgreen", width=3, tags="net")
            self.after(100, self.animate_net)

    def animate_net(self):
        if self.net:
            self.canvas.move(self.net, 0, 5)  # Move net downwards to simulate catching
            if self.canvas.bbox(self.net)[3] > WINDOW_HEIGHT:
                self.canvas.delete(self.net)
                self.net = None

    def play_win_song(self):
        pygame.mixer.music.load(r"c:\Users\User\Downloads\orchestral-glory-241499.mp3")

        pygame.mixer.music.play()  # Play the song

    def move_fish_randomly(self):
        if self.game_over:
            return
        for fish_tag, _ in self.fishes:
            dx = random.choice([-40, -25, 0, 25, 40])
            dy = random.choice([-30, -20, 0, 20, 30])
            coords = self.canvas.bbox(fish_tag)
            if coords:
                x1, y1, x2, y2 = coords
                if 0 < x1 + dx < WINDOW_WIDTH - FISH_WIDTH and 100 < y1 + dy < WINDOW_HEIGHT - FISH_HEIGHT:
                    self.canvas.move(fish_tag, dx, dy)

    def update_game(self):
        elapsed = time.time() - self.start_time
        if elapsed >= GAME_DURATION:
            self.end_game()
            return

        if not self.game_over:
            self.move_fish_randomly()
            delay = random.randint(100, 300)
            self.after(delay, self.update_game)

    def end_game(self):
        self.game_over = True
        result_text = "You Win! 🐟" if self.win else "Wrong Fish! 😢"
        color = "white" if self.win else "black"
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                                text=result_text, font=("Arial", 28, "bold"), fill=color)

if __name__ == "__main__":
    app = FishClickGame()
    app.mainloop()
