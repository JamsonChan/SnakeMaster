import pygame, sys, time, random
from pygame.locals import *
from pathlib import Path, os
from coor_queue import Node, Queue
from item_stack import Stack
class SnakeMaster:
    def __init__(self): # 此初始化方法內的類別屬性，是在五道題目內會用到的所有類別屬性
        self.init_params()
        self.init_pygame()
        self.init_objects()
        self.init_images()
    def run(self): # 遊戲主程式
        while True:
            self.theme_loop()
            self.keyboard_input()
            self.check_input_valid()
            self.move()
            self.eat()
            self.activate()
            self.display()
            if self.is_dead():
                self.game_over()
            self.fps.tick(8 + self.speed//5)
    def theme_loop(self): # 循環播放背景音樂
        if not pygame.mixer.music.get_busy():
            while True:
                next_theme = self.theme_list[random.randrange(len(self.theme_list))]
                if next_theme != self.theme and next_theme.startswith("theme"):
                    self.theme = next_theme
                    self.play_theme(self.theme)
                    break
    def keyboard_input(self): # 偵測鍵盤輸入
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == ord("d") or event.key == K_RIGHT: self.input_dir = "right"
                if event.key == ord("a") or event.key == K_LEFT:  self.input_dir = "left"
                if event.key == ord("w") or event.key == K_UP:    self.input_dir = "up"
                if event.key == ord("s") or event.key == K_DOWN:  self.input_dir = "down"
                if event.key == K_SPACE:
                    if not self.backpack.isEmpty():
                        self.use_item()
                if event.key == K_ESCAPE: pygame.event.post(pygame.event.Event(QUIT))
    def check_input_valid(self): # 確認鍵盤輸入的方向是否有效 (若與上個方向相反，則無效)
        if (self.input_dir == "right" and self.dir != "left") or (self.input_dir == "left" and self.dir != "right") or \
           (self.input_dir == "up"    and self.dir != "down") or (self.input_dir == "down" and self.dir != "up"):
            self.dir = self.input_dir
    def move(self): # 根據方向移動蛇的坐標
        x = self.snake.rear.x
        y = self.snake.rear.y
        if self.dir == "right": x += self.g
        if self.dir == "left" : x -= self.g
        if self.dir == "up"   : y -= self.g
        if self.dir == "down" : y += self.g
        self.snake.deQueue()
        self.snake.enQueue(x, y)
    def eat(self): # 吃到東西
        self.eat_body()
        self.eat_food()
        self.eat_item()
        self.eat_event()
        self.eat_fruit_basket()
    def activate(self): # 啟動使用的道具或觸發的事件
        if self.item_BlackHole: # 黑洞
            if self.item == "BlackHole":
                self.item = None
                self.img_body = pygame.image.load(Path("src/image/snake/InvincibleBody.jpg")).convert_alpha()
                self.play_theme("Blackhole")
                self.t_BlackHole = time.time()
            if 20-(time.time()-self.t_BlackHole) <= 0:
                self.img_body = pygame.image.load(Path("src/image/snake/SnakeBody.jpg")).convert_alpha()
                self.item_BlackHole = False
            if self.snake.rear.x < 0           : self.snake.rear.x += self.width
            if self.snake.rear.x >= self.width : self.snake.rear.x -= self.width
            if self.snake.rear.y < 0           : self.snake.rear.y += self.height
            if self.snake.rear.y >= self.height: self.snake.rear.y -= self.height
        if self.item_Gamble: # 賭博
            self.item_Gamble = False
            if random.randrange(10) % 10 == 0:
                self.game_over()
            else:
                self.score += self.spf*10
                self.play_effect("got_big_score")
        if self.item_Brake: # 剎車
            self.item_Brake = False
            self.speed //= 2
            self.play_effect("slow_down")
        if self.item_FruitBasket: # 水果籃
            self.item_FruitBasket = False
            self.fruit_basket_list = self.food_list[:]
            self.fruitBasketPos = []
            for i in range(len(self.fruit_basket_list)):
                x = random.randrange(self.width//self.g)*self.g
                y = random.randrange(self.height//self.g)*self.g
                self.fruitBasketPos.append([x, y])
            self.play_effect("fruit_basket")
        if self.event_GoldSnake: # 黃金蛇
            if self.event == "GoldSnake":
                self.event = None
                self.play_effect("gold_snake")
                self.t_GoldSnake = time.time()
            if 20-(time.time()-self.t_GoldSnake) <= 0:
                self.event_GoldSnake = False
            self.auto_snake(self.GoldSnake)
            cur = self.GoldSnake.rear
            while cur:
                if cur.x == self.snake.rear.x and cur.y == self.snake.rear.y:
                    self.score += self.spf
                    self.play_effect("got_score")
                    break
                cur = cur.pre
        if self.event_BoneSnake: #骷髏蛇
            if self.event == "BoneSnake":
                self.event = None
                self.play_effect("bone_snake")
                self.t_BoneSnake = time.time()
            if 20-(time.time()-self.t_BoneSnake) <= 0:
                self.event_BoneSnake = False
            self.auto_snake(self.BoneSnake)
            cur = self.snake.rear
            while cur:
                if cur.x == self.BoneSnake.rear.x and cur.y == self.BoneSnake.rear.y:
                    self.score -= self.spf//5
                    self.play_effect("lose_score")
                    break
                cur = cur.pre
    def display(self): # 刷新影像
        # 背景
        self.blit_map()
        # 蛇身
        cur = self.snake.rear.pre
        while cur:
            self.blit_image("body", cur.x, cur.y, self.g, self.g)
            cur = cur.pre
        # 蛇頭
        if self.snake.rear.x < self.width:
            self.blit_image("head", self.snake.rear.x, self.snake.rear.y, self.g, self.g)
        # 黃金蛇
        if self.event_GoldSnake:
            cur = self.GoldSnake.rear.pre
            while cur:
                self.blit_image("GoldSnake_body", cur.x, cur.y, self.g, self.g)
                cur = cur.pre
            self.blit_image("GoldSnake_head", self.GoldSnake.rear.x, self.GoldSnake.rear.y, self.g, self.g)
        # 骷髏蛇
        if self.event_BoneSnake:
            cur = self.BoneSnake.rear.pre
            while cur:
                self.blit_image("BoneSnake_body", cur.x, cur.y, self.g, self.g)
                cur = cur.pre
            self.blit_image("BoneSnake_head", self.BoneSnake.rear.x, self.BoneSnake.rear.y, self.g, self.g)
        # 食物
        self.blit_image(self.food, self.foodPos.x, self.foodPos.y, self.g, self.g)
        # 水果禮盒
        for i in range(len(self.fruit_basket_list)):
            self.blit_image(self.fruit_basket_list[i], self.fruitBasketPos[i][0], self.fruitBasketPos[i][1], self.g, self.g)
        # 黃色問號方塊
        if self.itemBoxPos != None:
            self.blit_image("itemBox", self.itemBoxPos[0], self.itemBoxPos[1], self.g, self.g)
        # 紅色問號方塊
        for i in range(len(self.eventBox_list)):
            self.blit_image("eventBox", self.eventBox_list[i][0], self.eventBox_list[i][1], self.g, self.g)
        # 狀態欄
        self.blit_status_bar()

        pygame.display.flip()
    def is_dead(self): # 判斷是否跑出遊戲介面以外
        return (self.snake.rear.x == self.width or self.snake.rear.x < 0) or \
               (self.snake.rear.y == self.height or self.snake.rear.y < 0)
    def game_over(self): # Game Over 畫面
        step = 1
        
        while True:
            if step == 1:
                self.play_theme("game_over1")
                step = 2
            elif step == 2 and not pygame.mixer.music.get_busy():
                self.play_effect("Explode")
                for i in range(1,6):
                    self.blit_map()
                    if self.snake.rear != self.snake.front:
                        self.blit_image("head", self.snake.rear.x, self.snake.rear.y, self.g, self.g)
                    cur = self.snake.rear.pre
                    while cur != self.snake.front and cur != None:
                        self.blit_image("body", cur.x, cur.y, self.g, self.g)
                        cur = cur.pre
                    self.blit_image(f"explosion{i}", self.snake.front.x, self.snake.front.y, self.g, self.g)
                    self.blit_status_bar()
                    pygame.display.flip()
                    self.fps.tick(50)
                self.snake.deQueue()
                self.score += self.spf

                if self.snake.front == None and self.snake.rear == None:
                    self.blit_image("GameOver", self.width/4, self.height/4, 16*self.g, 8*self.g)
                    self.blit_status_bar()
                    pygame.display.flip()
                    pygame.event.clear()
                    step = 3
                    self.play_theme("game_over2")
            elif step == 3:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE: pygame.event.post(pygame.event.Event(QUIT))
                        if event.key == K_RETURN: step = 4
            elif step == 4:
                self.__init__()
                break
    def init_params(self): # 基本參數設定
        self.g = 30 # 每方格寬度(30px)
        self.speed = 0     # 遊戲增加速度
        self.prob = 25     # 吃完食物後生成方塊的機率(單位是%)
        self.score = 0     # 初始分數
        self.spf = 10      # 每個食物的分數(會依食用次數增加)(score per food)
        self.satiety = 0   # 吃食物的次數(用來動態增加 self.spf)
        self.dir = "right" # 初始移動方向
        self.input_dir = None  # 鍵盤輸入的移動方向
        self.screen_width  = 1140  # 視窗寬度
        self.screen_height = 540   # 視窗高度
        self.width  = 960  # 遊戲主介面(地圖)寬度
        self.height = 540  # 遊戲主介面(地圖)高度
    def init_pygame(self): # 初始化 pygame
        pygame.init()
        self.fps = pygame.time.Clock() # 初始化遊戲刷新物件
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height)) # 設定視窗寬高
        pygame.display.set_icon(pygame.image.load(Path("src/image/other/icon.jpg"))) # 視窗圖示
        pygame.display.set_caption("Snake Master") # 視窗標題
        pygame.mixer.init() # 初始化 pygame 音樂播放器
    def init_objects(self): # 初始化物件參數
        # 初始化蛇佇列
        self.snake = Queue()
        self.create_snake("snake", 0, 9, 3) # 初始化玩家蛇佇列
        self.GoldSnake = Queue()
        self.create_snake("GoldSnake", 10, 10, 6) # 初始化黃金蛇佇列
        self.BoneSnake = Queue()
        self.create_snake("BoneSnake", 10, 10, 6) # 初始化骷髏蛇佇列
        # 初始化背包堆疊，高度為3，代表最多只能存放3個道具
        self.backpack = Stack(3)
        # 初始化物件名稱列表
        self.map_list   = [map.split(".")[0] for map in os.listdir(Path("src/image/map"))]
        self.food_list  = [food.split(".")[0] for food in os.listdir(Path("src/image/food"))]
        self.theme_list = [theme.split(".")[0] for theme in os.listdir(Path("src/sound/theme"))]
        self.item_list  = ["BlackHole", "Brake", "FruitBasket", "Gamble"]
        # 初始化方塊位置(皆以[x, y]來表示)
        self.itemBoxPos = None # 儲存道具方塊座標的 list，未顯示時是None (同時只會存在 1 個)
        self.eventBox_list = list() # 儲存事件方塊座標的 list[list] (同時可存在多個)
        self.fruit_basket_list = list() # 儲存水果籃內水果座標的 list[list]
        # 選擇食物
        self.food = None
        self.select_food()
        self.theme = None
        # 初始化物件座標
        self.foodPos = Node(self.width//2, self.height//2)
        self.backpackPos = [[34*self.g, 14.8*self.g], [34*self.g, 11.6*self.g], [34*self.g, 8.4*self.g]]
        self.fruitBasketPos = list()
        # 初始化黃金、骷髏蛇狀態、事件參數
        self.event = None
        self.event_GoldSnake = False
        self.event_BoneSnake = False
        # 初始化道具狀態 (預設都是False，吃到道具方塊後，使用道具才會讓對應布林值參數變成True，並啟動道具效果)
        self.item = None
        self.item_BlackHole = False
        self.item_Gamble = False
        self.item_Brake = False
        self.item_FruitBasket = False
    def init_images(self): # 建立所有圖片物件
        self.img_StatusBar = pygame.image.load(Path("src/image/other/StatusBar.jpg")).convert_alpha()
        for i in range(1,6):
            exec(f"self.img_explosion{i} = pygame.image.load(Path('src/image/other/explosion{i}.jpg')).convert_alpha()")
        self.img_GameOver = pygame.image.load(Path("src/image/other/GameOver.jpg")).convert_alpha()
        self.img_itemBox = pygame.image.load(Path("src/image/other/itemBox.jpg")).convert_alpha()
        self.img_eventBox = pygame.image.load(Path("src/image/other/eventBox.jpg")).convert_alpha()
        self.img_head = pygame.image.load(Path("src/image/snake/SnakeHead.jpg")).convert_alpha()
        self.img_body = pygame.image.load(Path("src/image/snake/SnakeBody.jpg")).convert_alpha()
        self.img_BoneSnake_head = pygame.image.load(Path("src/image/snake/BoneSnakeHead.jpg")).convert_alpha()
        self.img_BoneSnake_body = pygame.image.load(Path("src/image/snake/BoneSnakeBody.jpg")).convert_alpha()
        self.img_GoldSnake_head = pygame.image.load(Path("src/image/snake/GoldSnakeHead.jpg")).convert_alpha()
        self.img_GoldSnake_body = pygame.image.load(Path("src/image/snake/GoldSnakeBody.jpg")).convert_alpha()
        for food in self.food_list:
            exec(f"self.img_{food} = pygame.image.load(Path('src/image/food/{food}.jpg')).convert_alpha()")
        for item in self.item_list:
            exec(f"self.img_{item} = pygame.image.load(Path('src/image/item/{item}.jpg')).convert_alpha()")
        for i in range(1, len(self.map_list)+1):
            exec(f"self.img_Map{i} = pygame.image.load(Path('src/image/map/Map{i}.jpg')).convert_alpha()")
        self.cur_Map = f"Map{self.spf//10}"
    def eat_body(self): # 吃到玩家蛇的身體
        cur = self.snake.rear.pre
        while cur:
            if (cur.x == self.snake.rear.x) and (cur.y == self.snake.rear.y):
                self.snake.front = cur.next
                cur.next.pre = None
                self.play_effect("eat_body")
                break
            cur = cur.pre
    def eat_food(self): # 吃掉食物 (同時生成下個食物、機率性生成道具(黃色問號)和事件(紅色問號)方塊)
        if self.snake.rear.x == self.foodPos.x and self.snake.rear.y == self.foodPos.y: # 若吃掉食物，則重新生成食物
            self.satiety += 1
            self.speed += 1
            self.spf = 10 + ((self.satiety-1)//10)*10
            self.score += self.spf
            self.play_effect("eat_food")
            x = random.randrange(1, self.width//self.g)
            y = random.randrange(1, self.height//self.g)
            self.foodPos.x = x*self.g
            self.foodPos.y = y*self.g

            self.select_food() # 隨機選擇新的食物
            self.add_tail() # 因為吃掉食物，加一個節點到 snake 尾端

            # 隨著吃掉食物，會有 20% 機率生成問號方塊
            p = 100//self.prob
            if random.randrange(p) % p == 0 and self.itemBoxPos == None:
                self.itemBoxPos = list()
                x = random.randrange(1, self.width//self.g)*self.g
                y = random.randrange(1, self.height//self.g)*self.g
                self.itemBoxPos.extend([x, y])
            if random.randrange(p) % p == 0:
                x = random.randrange(1, self.width//self.g)*self.g
                y = random.randrange(1, self.height//self.g)*self.g
                self.eventBox_list.append([x, y])
    def eat_item(self): # 吃到道具方塊(黃色問號)即獲得道具
        if self.itemBoxPos != None:
            if self.snake.rear.x == self.itemBoxPos[0] and self.snake.rear.y == self.itemBoxPos[1]:
                self.play_effect("eat_item")
                self.itemBoxPos = None
                item = self.item_list[random.randrange(len(self.item_list))]
                self.backpack.push(item)
    def eat_event(self): # 吃掉事件方塊(紅色問號)
        for i in range(len(self.eventBox_list)):
            if self.snake.rear.x == self.eventBox_list[i][0] and self.snake.rear.y == self.eventBox_list[i][1]:
                del self.eventBox_list[i]
                event = random.randrange(7)
                if event == 0: # 加速
                    self.speed *= 1.2
                    self.play_effect("speed_up")
                elif event == 1: # 減速
                    self.speed /= 1.2
                    self.play_effect("slow_down")
                elif event == 2: # 加分
                    self.score += self.spf*5
                    self.play_effect("got_big_score")
                elif event == 3: # 扣分
                    self.score -= self.spf*5
                    self.play_effect("lose_big_score")
                elif event == 4: # 召喚骷髏蛇(扣分蛇)
                    self.event = "BoneSnake"
                    self.event_BoneSnake = True
                elif event == 5: # 召喚黃金蛇(加分蛇)
                    self.event = "GoldSnake"
                    self.event_GoldSnake = True
                elif event == 6: # 頭尾反轉
                    cur = self.snake.front
                    if   cur.x - cur.next.x > 0: self.dir = self.input_dir = "right"
                    elif cur.x - cur.next.x < 0: self.dir = self.input_dir = "left"
                    elif cur.y - cur.next.y > 0: self.dir = self.input_dir = "down"
                    elif cur.y - cur.next.y < 0: self.dir = self.input_dir = "up"
                    self.snake.reverse()
                    self.play_effect("reverse")
                return 
    def eat_fruit_basket(self): # 吃掉水果籃噴發出來的食物
        for i in range(len(self.fruit_basket_list)):
            if (self.snake.rear.x == self.fruitBasketPos[i][0]) and (self.snake.rear.y == self.fruitBasketPos[i][1]):
                del self.fruit_basket_list[i]
                del self.fruitBasketPos[i]
                self.satiety += 1
                self.spf = 10 + ((self.satiety-1)//10)*10
                self.score += self.spf
                self.add_tail()
                self.play_effect("eat_food")
                break
    def add_tail(self): # 加一個節點到玩家蛇的尾端(此方法是在蛇吃掉食物的時候被呼叫)
        cur = self.snake.front.next
        x = cur.pre.x*2 - cur.x
        y = cur.pre.y*2 - cur.y
        cur = cur.pre
        cur.pre = Node(x, y)
        cur.pre.next = self.snake.front
        self.snake.front = cur.pre
    def use_item(self): # 使用道具
        self.item = self.backpack.top.item
        self.backpack.pop()
        exec(f"self.item_{self.item} = True")
    def select_food(self): # 隨機選擇下個食物(在 eat_food 中上個食物被吃掉時被呼叫)
        while True:
            next_food = self.food_list[random.randrange(len(self.food_list))]
            if next_food != self.food:
                self.food = next_food
                break 
    def create_snake(self, name, x, y, length): # 快速建立黃金蛇、骷髏蛇佇列
        for i in range(length):
            exec(f"self.{name}.enQueue({x+i}*self.g, {y}*self.g)")
    def auto_snake(self, snake): # 讓黃金蛇與骷髏蛇自動移動
        snake_ch_x = snake.rear.x
        snake_ch_y = snake.rear.y
        straight_x = set()
        straight_y = set()
        cur = snake.rear
        while cur:
            straight_x = straight_x | {cur.x}
            straight_y = straight_y | {cur.y}
            cur = cur.pre
        xx = snake.rear.x - snake.rear.pre.x
        yy = snake.rear.y - snake.rear.pre.y
        if len(straight_x)==1 or len(straight_y)==1:
            dir = random.randrange(2)
            if   xx == 0 and dir == 0: snake_ch_x += self.g
            elif xx == 0 and dir == 1: snake_ch_x -= self.g
            elif yy == 0 and dir == 0: snake_ch_y += self.g
            elif yy == 0 and dir == 1: snake_ch_y -= self.g
        else:
            if   xx > 0: snake_ch_x += self.g
            elif xx < 0: snake_ch_x -= self.g
            elif yy > 0: snake_ch_y += self.g
            elif yy < 0: snake_ch_y -= self.g

        if snake_ch_x < 0           : snake_ch_x += self.width
        if snake_ch_x >= self.width : snake_ch_x -= self.width
        if snake_ch_y < 0           : snake_ch_y += self.height
        if snake_ch_y >= self.height: snake_ch_y -= self.height
        snake.enQueue(snake_ch_x, snake_ch_y)
        snake.deQueue()
    def play_theme(self, theme): # 播放背景音樂
        pygame.mixer.music.load(Path(f"src/sound/theme/{theme}.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()
    def play_effect(self, effect): # 播放音效
        sound = pygame.mixer.Sound(Path(f"src/sound/effect/{effect}.mp3"))
        sound.set_volume(0.7)
        sound.play()
    def blit_image(self, name, coor_x = 0, coor_y = 0, size_x = 0, size_y = 0): # 繪製圖片
        exec(f"self.img_{name} = pygame.transform.scale(self.img_{name}, size=(size_x, size_y))")
        exec(f"self.screen.blit(self.img_{name}, (coor_x, coor_y))")
    def blit_rect(self, data, coor_x = 0, coor_y = 0, font_size = 80, color = (0, 0, 0)): # 繪製矩形區塊
        self.Font = pygame.font.SysFont("", font_size)
        self.Surf = self.Font.render(str(data), True, color)
        self.Rect = self.Surf.get_rect()
        self.Rect.center = (coor_x, coor_y)
        self.screen.blit(self.Surf, self.Rect)
    def blit_map(self): # 繪製地圖
        if self.spf > 100:
            new_Map = "Map10"
        else:
            new_Map = f"Map{self.spf//10}"
        if self.cur_Map != new_Map:
            self.cur_Map = new_Map
            self.play_effect("map_change")
        self.blit_image(new_Map, 0, 0, self.width, self.height) 
    def blit_status_bar(self): # 繪製狀態欄
        # 狀態欄
        self.blit_image("StatusBar", 960, 0, 180, self.screen_height)
        # 分數
        self.blit_rect(self.score, 35*self.g, 1.87*self.g, font_size = 50, color = (238, 0, 0))
        # 速度
        self.blit_rect(int(8 + self.speed)-7, 35*self.g, 4.13*self.g, font_size = 50, color = (178, 58, 238))
        # 長度
        self.blit_rect(self.snake.len(), 35*self.g, 6.28*self.g, font_size = 50, color = (50, 205, 50))
        # 道具欄
        cur = self.backpack.top
        for i in range(self.backpack.len()):
            exec(f"self.img_item = pygame.transform.scale(self.img_{cur.item}, (self.g*2, self.g*2))")
            self.screen.blit(self.img_item, (self.backpackPos[i][0], self.backpackPos[i][1]))
            cur = cur.next