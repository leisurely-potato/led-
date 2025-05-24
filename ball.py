import pygame
import sys
import random

# 初始化Pygame
pygame.init()

# 设置窗口尺寸
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("弹跳小球游戏")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
COLORS = [RED, GREEN, BLUE, (255, 255, 0), (0, 255, 255), (255, 0, 255)]

class Ball:
    def __init__(self):
        self.radius = random.randint(20, 40)
        self.x = random.randint(self.radius, width - self.radius)
        self.y = random.randint(self.radius, height - self.radius)
        self.dx = random.choice([-4, -3, -2, 2, 3, 4])
        self.dy = random.choice([-4, -3, -2, 2, 3, 4])
        self.color = random.choice(COLORS)
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        # 检查碰到左右边界
        if self.x <= self.radius or self.x >= width - self.radius:
            self.dx = -self.dx
            self.color = random.choice(COLORS)
        
        # 检查碰到上下边界
        if self.y <= self.radius or self.y >= height - self.radius:
            self.dy = -self.dy
            self.color = random.choice(COLORS)
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

# 创建多个球
balls = [Ball() for _ in range(5)]

# 游戏主循环
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 按空格键添加新的球
                balls.append(Ball())
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
    
    # 清空屏幕
    screen.fill(BLACK)
    
    # 移动并绘制所有球
    for ball in balls:
        ball.move()
        ball.draw()
    
    # 更新屏幕
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)