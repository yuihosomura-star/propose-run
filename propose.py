import pyxel
import math
import random

W, H = 200, 200

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

class Boy:
    def __init__(self):
        self.x = 40
        self.y = 100
        self.r = 4
        self.speed = 1.6
        self.dash_cd = 0 

    def update(self):
        vx = 0
        vy = 0
        if pyxel.btn(pyxel.KEY_LEFT):
            vx -= 1
        if pyxel.btn(pyxel.KEY_RIGHT):
            vx += 1
        if pyxel.btn(pyxel.KEY_UP):
            vy -= 1
        if pyxel.btn(pyxel.KEY_DOWN):
            vy += 1

       
        if vx != 0 and vy != 0:
            vx *= 0.7071
            vy *= 0.7071

        sp = self.speed

       
        if self.dash_cd > 0:
            self.dash_cd -= 1
        if pyxel.btnp(pyxel.KEY_SPACE) and self.dash_cd == 0:
            self.dash_cd = 30 
        if self.dash_cd > 20:
            sp = 3.0

        self.x = clamp(self.x + vx * sp, 6, W - 6)
        self.y = clamp(self.y + vy * sp, 6, H - 6)

    def draw(self):
        
        pyxel.circ(self.x, self.y, self.r, 1)       
        pyxel.line(self.x, self.y + 4, self.x, self.y + 10, 1) 
        pyxel.line(self.x, self.y + 6, self.x - 4, self.y + 9, 1) 
        pyxel.line(self.x, self.y + 6, self.x + 4, self.y + 9, 1) 
       
        pyxel.circ(self.x + 6, self.y + 8, 2, 8)   
        pyxel.line(self.x + 6, self.y + 10, self.x + 6, self.y + 14, 11)  


class Girl:
    def __init__(self):
        self.x = 160
        self.y = 100
        self.r = 4

       
        self.vx = 0.0
        self.vy = 0.0
        self.max_speed = 4.8     
        self.accel_base = 0.10   
        self.friction = 0.88      
        self.zig_phase = 0.0      
        self.panic = 0.0         

    def update(self, boy_x, boy_y):
        dx = self.x - boy_x
        dy = self.y - boy_y
        dist = (dx * dx + dy * dy) ** 0.5 + 1e-6

       
        self.panic = clamp((120 - dist) / 90, 0.0, 1.0)

       
        ux = dx / dist
        uy = dy / dist

       
        self.zig_phase += 0.25 + 0.9 * self.panic
        zx = -uy
        zy = ux
        zig = math.sin(self.zig_phase) * (0.15 + 0.55 * self.panic)

       
        tx = ux + zx * zig
        ty = uy + zy * zig
        tlen = (tx * tx + ty * ty) ** 0.5 + 1e-6
        tx /= tlen
        ty /= tlen

        
        accel = self.accel_base + 0.25 * self.panic
        vmax = 2.0 + (self.max_speed - 2.0) * self.panic

       
        margin = 18
        bx = 0.0
        by = 0.0
        if self.x < margin: bx += (margin - self.x) / margin
        if self.x > W - margin: bx -= (self.x - (W - margin)) / margin
        if self.y < margin: by += (margin - self.y) / margin
        if self.y > H - margin: by -= (self.y - (H - margin)) / margin
        if bx != 0.0 or by != 0.0:
            
            tx += bx * (0.8 + 1.2 * self.panic)
            ty += by * (0.8 + 1.2 * self.panic)
            tlen2 = (tx * tx + ty * ty) ** 0.5 + 1e-6
            tx /= tlen2
            ty /= tlen2

       
        if self.panic > 0.6 and pyxel.frame_count % 17 == 0 and random.random() < 0.35:
            tx, ty = -ty, tx  # 90度ターン

        
        self.vx = self.vx * self.friction + tx * accel
        self.vy = self.vy * self.friction + ty * accel

        
        sp = (self.vx * self.vx + self.vy * self.vy) ** 0.5 + 1e-6
        if sp > vmax:
            self.vx = self.vx / sp * vmax
            self.vy = self.vy / sp * vmax

       
        self.x = clamp(self.x + self.vx, 6, W - 6)
        self.y = clamp(self.y + self.vy, 6, H - 6)

    def respawn_far_from(self, bx, by):
        self.vx = 0.0
        self.vy = 0.0
        for _ in range(50):
            x = random.randint(20, W - 20)
            y = random.randint(20, H - 20)
            if math.hypot(x - bx, y - by) > 110:
                self.x, self.y = x, y
                return
        self.x, self.y = 160, 100

    def draw(self):
        pyxel.circ(self.x, self.y, self.r, 13)
        pyxel.line(self.x, self.y + 4, self.x, self.y + 10, 13)
        pyxel.line(self.x, self.y + 6, self.x - 4, self.y + 9, 13)
        pyxel.line(self.x, self.y + 6, self.x + 4, self.y + 9, 13)
        pyxel.line(self.x - 3, self.y - 2, self.x - 6, self.y + 2, 2)
        pyxel.line(self.x + 3, self.y - 2, self.x + 6, self.y + 2, 2)


class App:
    def __init__(self):
        pyxel.init(W, H, title="Bouquet Chase")
        pyxel.mouse(False)

        self.boy = Boy()
        self.girl = Girl()

        self.score = 0
        self.state = "play"   
        self.timer = 0

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.state == "play":
            self.boy.update()
            self.girl.update(self.boy.x, self.boy.y)

           
            d = math.hypot(self.boy.x - self.girl.x, self.boy.y - self.girl.y)
            if d < 10:
                self.score += 1
                self.state = "caught"
                self.timer = 45 
        else:
            self.timer -= 1
            if self.timer <= 0:
                self.girl.respawn_far_from(self.boy.x, self.boy.y)
                self.state = "play"

    def draw(self):
        pyxel.cls(6)

       
        for x in range(0, W, 20):
            pyxel.line(x, 0, x, H, 7)

        self.girl.draw()
        self.boy.draw()

        pyxel.text(5, 5, f"Score: {self.score}", 0)
        pyxel.text(5, 15, "Arrow keys: move  Space: dash  Q: quit", 0)

        if self.state == "caught":
            pyxel.text(60, 90, "You caught her! Bouquet delivered!", 8)
           
            for i in range(20):
                px = random.randint(40, 160)
                py = random.randint(60, 140)
                pyxel.pset(px, py, random.choice([7, 10, 11, 8]))


App()
