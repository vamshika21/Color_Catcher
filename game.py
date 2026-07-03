import tkinter as tk
import random
from tkinter import simpledialog, messagebox
import os

BALL_SIZE = 25
BASKET_W, BASKET_H = 100, 20   # slightly larger basket
SPEED = 3
# Modern, vibrant color palette
COLORS = ["#ff4757", "#2ed573", "#1e90ff", "#ffa502", "#ff6b81", "#9c88ff"]
LEADERBOARD_FILE = "leaderboard.txt"

BG_COLOR = "#1e1e2f"
PANEL_BG = "#2b2b36"
TEXT_COLOR = "#f1f2f6"
ACCENT_COLOR = "#00d2ff"

class ColorCatcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Catcher")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("500x700")
        
        # --- Title at top ---
        self.title_label = tk.Label(root, text="COLOR CATCHER",
                                    font=("Segoe UI", 24, "bold"),
                                    fg=ACCENT_COLOR, bg=BG_COLOR)
        self.title_label.pack(pady=15)
        
        # Bottom panel
        bottom_frame = tk.Frame(root, bg=PANEL_BG, bd=0)
        bottom_frame.pack(fill="x", side="bottom")

        # Game canvas
        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both", padx=20)
        
        # Stats Bar
        stats_frame = tk.Frame(bottom_frame, bg="#191924")
        stats_frame.pack(fill="x")
        
        self.info = tk.Label(stats_frame,
                             text="Score: 0    |    Lives: 3    |    Level: 1    |    Best: 0",
                             fg=TEXT_COLOR, bg="#191924", font=("Segoe UI", 12, "bold"), pady=10)
        self.info.pack(expand=True)
        
        # Controls Frame inside bottom panel
        controls_frame = tk.Frame(bottom_frame, bg=PANEL_BG)
        controls_frame.pack(pady=15)
        
        self.restart_btn = tk.Button(controls_frame, text="▶ START GAME",
                                     command=self.prepare_game,
                                     font=("Segoe UI", 12, "bold"),
                                     bg="#2ed573", fg="white", 
                                     activebackground="#26ba62", activeforeground="white",
                                     relief="flat", padx=15, pady=5, cursor="hand2")
        self.restart_btn.grid(row=0, column=0, padx=10)
        
        self.target_color = random.choice(COLORS)
        self.target_btn = tk.Button(controls_frame, text="Catch Me!",
                                    bg=self.target_color, fg="white",
                                    font=("Segoe UI", 12, "bold"),
                                    relief="flat", padx=20, pady=5, state="disabled", disabledforeground="white")
        self.target_btn.grid(row=0, column=1, padx=10)
        
        self.lb_btn = tk.Button(controls_frame, text="🏆 LEADERBOARD",
                                command=self.show_leaderboard,
                                font=("Segoe UI", 12, "bold"), 
                                bg="#ffa502", fg="white",
                                activebackground="#e59400", activeforeground="white",
                                relief="flat", padx=15, pady=5, cursor="hand2")
        self.lb_btn.grid(row=0, column=2, padx=10)
        
        # State variables
        self.score, self.lives, self.level, self.highscore = 0, 3, 1, 0
        self.balls = []
        self.running = False
        self.paused = False
        self.basket = None
        
        # Key bindings
        root.bind("<Left>", lambda e: self.move(-30))
        root.bind("<Right>", lambda e: self.move(30))
        root.bind("a", lambda e: self.move(-30))
        root.bind("d", lambda e: self.move(30))
        root.bind("<space>", lambda e: self.toggle_pause())
        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """Keep basket fixed size, only reposition when resized"""
        if self.basket:
            w = event.width
            h = event.height
            self.canvas.coords(self.basket,
                               w//2 - BASKET_W//2, h-60,
                               w//2 + BASKET_W//2, h-60 + BASKET_H)

    def prepare_game(self):
        """Countdown before start"""
        self.canvas.delete("all")
        self.restart_btn.config(state="disabled", bg="gray")
        self.countdown(3)

    def countdown(self, n):
        self.canvas.delete("all")
        if n > 0:
            self.canvas.create_text(self.canvas.winfo_width()//2,
                                    self.canvas.winfo_height()//2,
                                    text=str(n), fill=ACCENT_COLOR,
                                    font=("Segoe UI", 60, "bold"))
            self.root.after(1000, lambda: self.countdown(n-1))
        else:
            self.canvas.create_text(self.canvas.winfo_width()//2,
                                    self.canvas.winfo_height()//2,
                                    text="GO!", fill="#2ed573",
                                    font=("Segoe UI", 70, "bold"))
            self.root.after(800, self.start_game)

    def start_game(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        # Create a modern looking basket
        self.basket = self.canvas.create_rectangle(
            w//2 - BASKET_W//2, h-60,
            w//2 + BASKET_W//2, h-60 + BASKET_H,
            fill="#dfe4ea", outline=ACCENT_COLOR, width=3
        )
        
        self.score, self.lives, self.level = 0, 3, 1
        self.target_color = random.choice(COLORS)
        self.target_btn.config(bg=self.target_color, text="Target")
        self.update_stats()
        self.balls.clear()
        self.running, self.paused = True, False
        
        self.restart_btn.config(text="⏹ STOP GAME", bg="#ff4757", 
                                activebackground="#e84118", state="normal")
        self.tick()

    def update_stats(self):
        self.info.config(text=f"Score: {self.score}    |    Lives: {self.lives}    |    Level: {self.level}    |    Best: {self.highscore}")

    def move(self, dx):
        if self.running and not self.paused and self.basket:
            x1, y1, x2, y2 = self.canvas.coords(self.basket)
            w = self.canvas.winfo_width()
            if x1 + dx < 0:
                dx = -x1
            elif x2 + dx > w:
                dx = w - x2
            self.canvas.move(self.basket, dx, 0)

    def toggle_pause(self):
        if self.running:
            self.paused = not self.paused
            if not self.paused:
                self.canvas.delete("pause_text")
                self.tick()
            else:
                self.canvas.create_text(self.canvas.winfo_width()//2,
                                        self.canvas.winfo_height()//2,
                                        text="PAUSED", fill="white",
                                        font=("Segoe UI", 40, "bold"), tags="pause_text")

    def spawn_ball(self):
        w = self.canvas.winfo_width()
        color = random.choice(COLORS)
        x = random.randint(20, w - BALL_SIZE - 20)
        # Create ball with slight offset for outline to look nicer
        ball = self.canvas.create_oval(x, -BALL_SIZE, x+BALL_SIZE, 0, 
                                       fill=color, outline="white", width=2)
        self.balls.append((ball, color))

    def tick(self):
        if not self.running or self.paused:
            return
            
        spawn_rate = 0.03 + (self.level * 0.005)
        if random.random() < spawn_rate:
            self.spawn_ball()
            
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        
        for ball, color in self.balls[:]:
            self.canvas.move(ball, 0, SPEED + self.level*0.5 + self.score//40)
            bx1, by1, bx2, by2 = self.canvas.coords(ball)
            bx, by = (bx1+bx2)/2, by2
            bx1b, by1b, bx2b, by2b = self.canvas.coords(self.basket)
            
            if by >= by1b and bx1b < bx < bx2b:  # caught
                if color == self.target_color:
                    self.score += 10
                    self.flash_basket("#2ed573")  # Green flash
                    if self.score % 50 == 0:
                        self.level += 1
                        self.target_btn.config(text=f"Level {self.level}")
                else:
                    self.lives -= 1
                    self.flash_basket("#ff4757")  # Red flash
                
                self.canvas.delete(ball)
                self.balls.remove((ball, color))
                
                if random.random() < 0.2:
                    self.target_color = random.choice(COLORS)
                    self.target_btn.config(bg=self.target_color)
                    
            elif by > h:  # missed
                if color == self.target_color:
                    self.lives -= 1
                    self.flash_basket("#ffa502") # Orange flash on miss
                self.canvas.delete(ball)
                self.balls.remove((ball, color))
                
        self.update_stats()
        
        if self.lives > 0:
            self.root.after(20, self.tick)
        else:
            self.running = False
            self.highscore = max(self.highscore, self.score)
            self.target_btn.config(text="GAME OVER", bg=PANEL_BG)
            self.restart_btn.config(text="▶ RESTART", bg="#2ed573", activebackground="#26ba62")
            
            self.canvas.create_text(w//2, h//2 - 40, text="GAME OVER", 
                                    fill="#ff4757", font=("Segoe UI", 50, "bold"))
            self.canvas.create_text(w//2, h//2 + 30, text=f"Final Score: {self.score}", 
                                    fill="white", font=("Segoe UI", 24))
            
            # Ask name and save score
            self.root.after(1000, self.prompt_score)

    def prompt_score(self):
        name = simpledialog.askstring("Game Over", "Enter your name for the Leaderboard:", parent=self.root)
        if name:
            self.save_score(name, self.score)

    def flash_basket(self, color):
        self.canvas.itemconfig(self.basket, fill=color, outline="white")
        self.root.after(200, lambda: self.canvas.itemconfig(self.basket, fill="#dfe4ea", outline=ACCENT_COLOR))

    # Leaderboard
    def save_score(self, name, score):
        try:
            with open(LEADERBOARD_FILE, "a", encoding="utf-8") as f:
                f.write(f"{name}:{score}\n")
        except Exception as e:
            print(f"Error saving score: {e}")

    def show_leaderboard(self):
        if not os.path.exists(LEADERBOARD_FILE):
            messagebox.showinfo("🏆 Leaderboard", "No scores yet!", parent=self.root)
            return
        scores = []
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        n, s = line.strip().split(":")
                        scores.append((n, int(s)))
        except Exception as e:
            messagebox.showerror("Error", f"Could not read leaderboard: {e}", parent=self.root)
            return
            
        scores.sort(key=lambda x: x[1], reverse=True)
        top = "\n".join([f"{i+1}. {n} ➔ {s} pts" for i, (n, s) in enumerate(scores[:10])])
        messagebox.showinfo("🏆 Top 10 Players", top or "No scores yet!", parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    ColorCatcher(root)
    root.mainloop()
