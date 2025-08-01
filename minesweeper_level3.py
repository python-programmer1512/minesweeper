"""
지뢰찾기 팀
기존 지뢰찾기 게임은 임의의 타일에 주변 8칸의 지뢰개수를 알려주어 지뢰를 피해 모든 땅을 여는 게임이다.

게임 구성
기존에 지뢰가 1개 있었지만 플레이어에게 친화적인 지뢰(쓰레기), 플레이어에게 해로운 지뢰(자연 친화적인 무언가)가 존재하며, 친화적인 지뢰를 찾게 되면 점수를 얻게 되고 
반대로 해로운 지뢰를 찾게되면 목숨이 깎인다. (clear)

기존 지뢰찾기와 다르게 임의의 칸에 친화적인 지뢰 와 해로운 지뢰의 숫자가 색깔, 위치 구별을 통해 나타나 있다. (clear)
친화적인 지뢰 중에는 아이템이 숨어 있는데 이 아이템에는 해로운 지뢰를 탐지하는 아이템과, 회복을 할 수 있는 아이템으로 구성되어있으며, 추후 추가 될 수 있다. 
난이도에 따른 시간제한이 있으며, 기존의 n*m 사이즈의 격자판 지뢰찾기가 아닌 맵별 불규칙하게 생긴 지뢰찾기 격자판이 주어지며 테마도 바뀌게 된다. (clear)
(ex. 초원,공원, 설원, .... 등 개발 진행을 통해 추가될 예정이다.)

UI 
아직 정해진 것은 없지만 맵을 선택할 수 있는 창과 시작, 제시도 할 수 있는 버튼 등이 있을 예정이다. 또 플레이 화면 하단에 획득한 아이템이 뜨고 누르면 사용할 수 있게 되어있다.

이외 나머지 과정들은 개발 진행속도와 팀원들의 의견에 따라 추가될 수 있다.



"""


import sys
sys.setrecursionlimit(10**9)

from random import *
import pygame
import time
from collections import deque
from math import * 
from collections import deque
from pygame.locals import QUIT,KEYDOWN,K_LEFT,K_RIGHT,K_UP,K_DOWN,Rect,MOUSEBUTTONDOWN,K_SPACE,K_a,K_x,K_z,K_LCTRL,K_RCTRL,MOUSEBUTTONUP
pygame.init()

FPSCLOCK = pygame.time.Clock()
width=900
height=1050
size=(width,height)
SURFACE = pygame.display.set_mode(size)
color={
    "black":[0,0,0],
    "white":[255,255,255],
    "red":[255,0,0],
    "blue":[0,0,255],
    "yellow":[255,255,0],
    "green":[0,255,0],
    "gray":[192,192,192],
    "cyan":[0,183,235],
    "purple":[106,13,173],
    "orange":[249,146,69],
    "skyblue":[80,188,223],
    "whitegray":[214,213,203],
    }

QE=["white","red","blue","yellow","green","gray","purple"]
colorn=[QE[i%len(QE)]for i in range(100)]
dy=[-1,0,1,0,-1,-1,1,1]
dx=[0,1,0,-1,-1,1,1,-1]

"""
0~9 : 지뢰 수
11 : hate 지뢰
13 : good 지뢰 or item
12 : 벽 타일
"""
H_MINE=11
G_MINE=13
ITEM=14
WALL_TILE=12

# wall,g_mine_cnt,h_mine_cnt,time,radius,heart,item_cnt
mode=[[0,0,0,0,0,0],
      [[250,300],[1/20],[1/10,2/10],4,(1,1),3,1],
      [[100,150],[1/20],[2/10,5/20],4,(2,2),3,2],
      [[50,100],[1/25],[5/20,3/10],3,(3,3),3,3],
      ]
#self.g_mine_cnt=randint(1,int((self.tile_cnt-self.wall_cnt)*(1/40)+1))
        #self.h_mine_cnt=randint(int((self.tile_cnt-self.wall_cnt)*(2/10)),int((self.tile_cnt-self.wall_cnt)*(4/10)))


class interface():
    def __init__(self,t_pos,MOD):
        pygame.sprite.Sprite.__init__(self)
        self.SURFACE=SURFACE
        
        self.mode=MOD
        
        
        #heart
        self.heart_pos=(t_pos[0],t_pos[1]+10)
        self.heart_size=(50,50)
        self.heart_image=pygame.image.load("./minesweeper/heart.png").convert_alpha()
        self.heartbreak_image=pygame.image.load("./minesweeper/heartbreak_black.png").convert_alpha()
        self.heart_image=pygame.transform.scale(self.heart_image,self.heart_size)
        self.heart_mask=pygame.mask.from_surface(self.heart_image)
        self.heartbreak_image=pygame.transform.scale(self.heartbreak_image,self.heart_size)
        self.heartbreak_mask=pygame.mask.from_surface(self.heartbreak_image)
        
        #time
        self.playtime=0
        self.start_time=0
        self.time_pos=(self.heart_pos[0],self.heart_pos[1]+self.heart_size[1])
        self.time_size=40
        self.time_font = pygame.font.SysFont("arial", self.time_size, True, False)
        self.Time=0
        
        #score
        self.score_pos=(self.time_pos[0],self.time_pos[1]+self.time_size)
        self.score_size=30
        self.score_font = pygame.font.SysFont("arial", self.score_size, True, False)
        
             
        #item
        self.item_using=False
        self.using_item_image=pygame.image.load("./minesweeper/detecter_item.png").convert_alpha()
        self.using_item_size=(80,80)
        self.using_item_image=pygame.transform.scale(self.using_item_image,self.using_item_size)
        self.using_item_mask=pygame.mask.from_surface(self.using_item_image)
        self.using_item_pos=(t_pos[0]+400,t_pos[1]+20)
    
        
      
    def using_item_draw(self,item_cnt):
        for i in range(item_cnt):
            self.SURFACE.blit(self.using_item_image,[self.using_item_pos[0]+i*(self.using_item_size[0]+10),self.using_item_pos[1]])
        
    def time_draw(self):
        self.Time=self.playtime-(time.time()-self.start_time)
        text_Title=self.time_font.render(f"{int(self.Time//60)} : {round(self.Time%60,1)}", True, color["black"])
        Rect=text_Title.get_rect()
        Rect.x=self.time_pos[0]
        Rect.y=self.time_pos[1]
        self.SURFACE.blit(text_Title, Rect)
        
    def score_draw(self,score):
        text_Title=self.score_font.render(f"score : {score}", True, color["black"])
        Rect=text_Title.get_rect()
        Rect.x=self.score_pos[0]
        Rect.y=self.score_pos[1]
        self.SURFACE.blit(text_Title, Rect)
        
    def heart_draw(self,heart):
        if heart<=0:return 0
        if heart>0:
            for i in range(heart):
                self.SURFACE.blit(self.heart_image,[self.heart_pos[0]+i*((11/10)*self.heart_size[0]),self.heart_pos[1]])
        if 3-heart>0:
            for i in range(heart,3):
                self.SURFACE.blit(self.heartbreak_image,[self.heart_pos[0]+i*((11/10)*self.heart_size[0]),self.heart_pos[1]])
             
        return 1
    
    def game_start(self):
        self.start_time=time.time()
        self.playtime=10 * self.mode[3]
                   
class Map(pygame.sprite.Sprite):
    def __init__(self,MOD):
        pygame.sprite.Sprite.__init__(self)
        self.score=0
        self.heart=0
        self.mode=MOD
        self.map_pos = (100,130) # 맵 왼쪽 위 좌표
        self.tile_size = (35,35) # 타일 가로, 세로 길이
        self.map_size = (20,20) # 맵 가로, 세로 타일 수
        self.tile_cnt=self.map_size[0]*self.map_size[1] # 총 타일 수
        self.SURFACE=SURFACE
        self.h_map=[[-1 for i in range(self.map_size[0])]for g in range(self.map_size[1])]
        self.g_map=[[-1 for i in range(self.map_size[0])]for g in range(self.map_size[1])]
        self.cover=[[1 for i in range(self.map_size[0])]for g in range(self.map_size[1])]
        self.flag=[[0 for i in range(self.map_size[0])]for g in range(self.map_size[1])]
        self.draw_except_num=[0,H_MINE,WALL_TILE,G_MINE,ITEM]
        
        self.wall_idx=[randint(0,self.tile_cnt-1) for _ in range(randint(self.mode[0][0],self.mode[0][1]))]#[[10,10]]
        #self.wall=list(set(self.wall))
        self.wall_cnt=len(self.wall_idx)
        self.wall=[(self.wall_idx[i]//self.map_size[0],self.wall_idx[i]%self.map_size[0]) for i in range(self.wall_cnt)]
        for pos in self.wall:
            #print(pos)
            self.h_map[pos[1]][pos[0]],self.g_map[pos[1]][pos[0]]=WALL_TILE, WALL_TILE
        """
        0~9 : 지뢰 수
        11 : hate 지뢰
        13 : good 지뢰 or item
        12 : 벽 타일
        """
        
        #flag
        self.flag_image=pygame.image.load("./minesweeper/flag.png").convert_alpha()
        self.flag_image=pygame.transform.scale(self.flag_image,self.tile_size)
        self.flag_mask=pygame.mask.from_surface(self.flag_image)
        
        #text
        self.font = pygame.font.SysFont("arial", int(self.tile_size[1]/2), True, False)
        
        #item
        self.item_cnt=MOD[6]
        self.item_image=pygame.image.load("./minesweeper/detecter.png").convert_alpha()
        #print(self.tile_size)
        self.item_image=pygame.transform.scale(self.item_image,self.tile_size)
        self.item_mask=pygame.mask.from_surface(self.item_image)
        
        #mine
        self.h_mine_cnt=0
        self.g_mine_cnt=0
        
        ## good mine
        self.g_mine_image=pygame.image.load("./minesweeper/flower.png").convert_alpha()
        self.g_mine_image=pygame.transform.scale(self.g_mine_image,self.tile_size)
        self.g_mask=pygame.mask.from_surface(self.g_mine_image)
        
        ## hate mine
        self.h_mine_1_image=pygame.image.load("./minesweeper/trash_1.png").convert_alpha()
        self.h_mine_1_image=pygame.transform.scale(self.h_mine_1_image,self.tile_size)
        self.h_mask=pygame.mask.from_surface(self.h_mine_1_image)
        
        # wall
        self.wall_image=pygame.image.load("./minesweeper/wall.png").convert_alpha()
        self.wall_image=pygame.transform.scale(self.wall_image,self.tile_size)
        self.wall_mask=pygame.mask.from_surface(self.wall_image)
   
    def game_start(self):
        self.heart=self.mode[5]
        self.g_mine_cnt=randint(1,int((self.tile_cnt-self.wall_cnt)*(self.mode[1][0])+1))
        self.h_mine_cnt=randint(int((self.tile_cnt-self.wall_cnt)*(self.mode[2][0])),int((self.tile_cnt-self.wall_cnt)*(self.mode[2][1])))
        #print("CNT :",self.g_mine_cnt,self.h_mine_cnt)
        mine_list=[]
        for i in range(self.tile_cnt):
            if not i in self.wall_idx:
                mine_list.append(i)
        shuffle(mine_list)
        #print(self.wall_idx)
        #mine_list = sample(range(0,self.tile_cnt),self.h_mine_cnt+self.g_mine_cnt) # 1부터 100까지의 범위중에 10개를 중복없이 뽑겠다.
        for idx in mine_list[:self.h_mine_cnt]:
            pos=(idx//self.map_size[0],idx%self.map_size[0])
            #if pos in self.wall_idx:print("!",pos)
            self.h_map[pos[1]][pos[0]]=H_MINE
            
        for idx in mine_list[self.h_mine_cnt:self.h_mine_cnt+self.g_mine_cnt]:
            pos=(idx//self.map_size[0],idx%self.map_size[0])
            if randint(1,4)!=1:
                self.g_map[pos[1]][pos[0]]=G_MINE
                #if pos in self.wall_idx:print("!!",pos)
                #print("good mine")
                #print(pos)
            else:
                self.g_map[pos[1]][pos[0]]=ITEM
                #if pos in self.wall_idx:print("!!!",pos)
                #print(pos)
                #print("item")
                #print(pos)
            
            
            
        for i in range(self.map_size[1]):
            for j in range(self.map_size[0]):
                if self.h_map[i][j]!=WALL_TILE and self.g_map[i][j]!=WALL_TILE:
                    h_cnt=0
                    g_cnt=0
                    if self.h_map[i][j]!=H_MINE:
                        for h in range(8):
                            nx=j+dx[h]
                            ny=i+dy[h]
                            if 0<=nx<self.map_size[0] and 0<=ny<self.map_size[1]:
                                if self.h_map[ny][nx]==H_MINE:
                                    h_cnt+=1
                                    
                        self.h_map[i][j]=h_cnt
                                    
                    if self.g_map[i][j]!=G_MINE and self.g_map[i][j]!=ITEM:
                        for h in range(8):
                            nx=j+dx[h]
                            ny=i+dy[h]
                            if 0<=nx<self.map_size[0] and 0<=ny<self.map_size[1]:
                                if self.g_map[ny][nx]==G_MINE or self.g_map[ny][nx]==ITEM:
                                    g_cnt+=1
                                    
                        self.g_map[i][j]=g_cnt       
    
    def frame_draw(self):
        for i in range(self.map_size[1]+1):
            pygame.draw.line(self.SURFACE,color["black"],[self.map_pos[0],self.map_pos[1]+self.tile_size[1]*i],\
                             [self.map_pos[0]+self.tile_size[0]*self.map_size[0],self.map_pos[1]+self.tile_size[1]*i],2)
            
        for i in range(self.map_size[0]+1):
            pygame.draw.line(self.SURFACE,color["black"],[self.map_pos[0]+self.tile_size[0]*i,self.map_pos[1]],\
                             [self.map_pos[0]+self.tile_size[0]*i,self.map_pos[1]+self.tile_size[1]*self.map_size[1]],2)
            
    def cover_draw(self):
        for i in range(self.map_size[1]):
            for j in range(self.map_size[0]):
                
                not_mine=True
                    
                if self.h_map[i][j]==H_MINE:
                    self.SURFACE.blit(self.h_mine_1_image,\
                        [self.map_pos[0]+self.tile_size[0]*j,self.map_pos[1]+self.tile_size[1]*i,self.tile_size[0],self.tile_size[1]])
                
                if self.g_map[i][j]==G_MINE:
                    self.SURFACE.blit(self.g_mine_image,\
                        [self.map_pos[0]+self.tile_size[0]*j,self.map_pos[1]+self.tile_size[1]*i,self.tile_size[0],self.tile_size[1]])

                if self.g_map[i][j]==ITEM:
                    self.SURFACE.blit(self.item_image,\
                        [self.map_pos[0]+self.tile_size[0]*j,self.map_pos[1]+self.tile_size[1]*i,self.tile_size[0],self.tile_size[1]])



                if not self.h_map[i][j] in self.draw_except_num:#!=0 and self.h_map[i][j]!=11 and self.h_map[i][j]!=13:
                    
                    ## 위쪽
                    text_Title=self.font.render(str(self.h_map[i][j]), True, color["red"])
                    Rect=text_Title.get_rect()
                    Rect.center=(self.map_pos[0]+self.tile_size[0]*j + self.tile_size[0]/2 + self.tile_size[0]/4,
                                self.map_pos[1]+self.tile_size[1]*i + self.tile_size[1]/2 - self.tile_size[1]/4)
                    self.SURFACE.blit(text_Title, Rect)
                
                else:
                    not_mine=False
                    
                if not self.g_map[i][j] in self.draw_except_num:
                    
                    ## 아래 쪽
                    text_Title=self.font.render(str(self.g_map[i][j]), True, color["blue"])
                    Rect=text_Title.get_rect()
                    Rect.center=(self.map_pos[0]+self.tile_size[0]*j + self.tile_size[0]/2 - self.tile_size[0]/4,
                                self.map_pos[1]+self.tile_size[1]*i + self.tile_size[1]/2 + self.tile_size[1]/4)
                    self.SURFACE.blit(text_Title, Rect)
                    
                else:
                    not_mine=False



                if not_mine:
                    pygame.draw.line(self.SURFACE,color["black"],
                    [self.map_pos[0]+self.tile_size[0]*j,self.map_pos[1]+self.tile_size[1]*i],
                    [self.map_pos[0]+self.tile_size[0]*(j+1),self.map_pos[1]+self.tile_size[1]*(i+1)],3
                    )

                # cover
                
                if self.cover[i][j]==1 and self.h_map[i][j]!=WALL_TILE and self.g_map[i][j]!=WALL_TILE:
                    pygame.draw.rect(self.SURFACE, color["skyblue"], \
                        [self.map_pos[0]+self.tile_size[0]*j,self.map_pos[1]+self.tile_size[1]*i,self.tile_size[0],self.tile_size[1]])
                    
                if self.h_map[i][j]==WALL_TILE or self.g_map[i][j]==WALL_TILE:
                    self.SURFACE.blit(self.wall_image,\
                        [self.map_pos[0]+self.tile_size[0]*j,self.map_pos[1]+self.tile_size[1]*i,self.tile_size[0],self.tile_size[1]])
                         
    def flag_draw(self):
        for i in range(self.map_size[1]):
            for j in range(self.map_size[0]):
                if self.flag[i][j]==1:
                    self.SURFACE.blit(self.flag_image,[self.map_pos[0]+self.tile_size[0]*j,self.map_pos[1]+self.tile_size[1]*i])
                    
    def click_pos(self,pos):
        return ((pos[0]-self.map_pos[0])//self.tile_size[0],(pos[1]-self.map_pos[1])//self.tile_size[1])
    
    def dfs(self,pos):
        if self.h_map[pos[1]][pos[0]]!=0 or self.g_map[pos[1]][pos[0]]!=0:return
        
        self.cover[pos[1]][pos[0]]=0
        for i in range(8):
            nx=pos[0]+dx[i]
            ny=pos[1]+dy[i]
            if 0<=nx<self.map_size[0] and 0<=ny<self.map_size[1]:
                if self.cover[ny][nx]==1 and self.flag[ny][nx]==0:
                    if self.g_map[ny][nx]==WALL_TILE or self.h_map[ny][nx]==WALL_TILE:continue
                    if self.h_map[ny][nx]==0 and self.g_map[ny][nx]==0:
                        self.dfs((nx,ny))
                    elif 1<=self.h_map[ny][nx]<=8 or 1<=self.g_map[ny][nx]<=8:
                        if self.h_map[ny][nx]!=11 and self.g_map[ny][nx]!=G_MINE:
                            self.cover[ny][nx]=0
                    
    
    def cover_off(self,pos):
        if 0<=pos[0]<self.map_size[0] and 0<=pos[1]<self.map_size[1]:
            if self.cover[pos[1]][pos[0]]==1:
                if self.flag[pos[1]][pos[0]]==1:
                    self.flag[pos[1]][pos[0]]=0
                else:
                    self.dfs(pos)
                    self.cover[pos[1]][pos[0]]=0
                    if self.h_map[pos[1]][pos[0]]==H_MINE:
                        self.heart-=1
                    if self.g_map[pos[1]][pos[0]]==G_MINE:
                        self.heart+=1
                    if self.g_map[pos[1]][pos[0]]==ITEM:
                        self.item_cnt+=1
                        
                    
            
    def flag_on(self,pos):
        if 0<=pos[0]<=self.map_size[0] and 0<=pos[1]<=self.map_size[1] and self.flag[pos[1]][pos[0]]==0 and self.cover[pos[1]][pos[0]]==1 and not pos in self.wall:
            self.flag[pos[1]][pos[0]]=1
            
class GAMESYSTEM(Map,interface,pygame.sprite.Sprite):
    def __init__(self,MOD):
        pygame.sprite.Sprite.__init__(self)
        Map.__init__(self,MOD)
        
        time_pos=(self.map_pos[0],
                  self.map_pos[1]+self.tile_size[1]*self.map_size[1])
        interface.__init__(self,time_pos,MOD)      
        self.finish=0
        self.start=0
        self.finish_time=0
        
    def check_flag(self):
        cnt=0
        for i in range(self.map_size[1]):
            for j in range(self.map_size[0]):
                if self.flag[i][j]==1:
                    if self.h_map[i][j]==H_MINE:
                        cnt+=1
                    else:
                        cnt-=1
                        
        return cnt
        
    def game_start(self):
        Map.game_start(self)
        interface.game_start(self)
        self.finish=0
        self.start=1
        
    def gameover(self):
        self.finish=2
        
    def item_use(self,A):
        if self.item_using:return
        for i in range(self.item_cnt):
            rect=self.using_item_image.get_rect()
            rect.center=(self.using_item_pos[0]+i*(self.using_item_size[0]+10)+self.using_item_size[0]/2,
                         self.using_item_pos[1]+self.using_item_size[1]/2)
            mask=self.using_item_image_mask=pygame.mask.from_surface(self.using_item_image)
            B=Virtual_Object([self.using_item_image,rect,mask])
            if pygame.mouse.get_pressed()[0] and pygame.sprite.collide_mask(A,B):
                self.item_cnt-=1
                self.item_using=True
                return
            #self.SURFACE.blit(self.using_item_image,[self.using_item_pos[0]+i*(self.using_item_size[0]+10),self.using_item_pos[1]])
        
    def detect(self,pos,radius):
        for y in range(-1*radius[1],1*radius[1]+1):
            for x in range(-1*radius[0],1*radius[0]+1):
                if 0<=pos[0]+x<self.map_size[0] and 0<=pos[1]+y<self.map_size[1]:
                    if self.h_map[pos[1]+y][pos[0]+x]==H_MINE and self.cover[pos[1]+y][pos[0]+x]==1:
                        super().flag_on((pos[0]+x,pos[1]+y))
                        
        
    
    def draw(self,Gameclear):
        super().cover_draw()
        super().frame_draw()
        super().flag_draw()
        super().time_draw()
        super().using_item_draw(self.item_cnt)
        #super().score_draw(self.score)
        if not super().heart_draw(self.heart):
            if Gameclear==0:
                self.gameover()
            
    def clear_condition(self):
        for i in range(self.map_size[1]):
            for j in range(self.map_size[0]):
                if self.h_map[i][j]==H_MINE:
                    if self.flag[i][j]==1:
                        continue
                    
                        
                else:
                    if self.g_map[i][j]!=G_MINE and self.g_map[i][j]!=ITEM and self.g_map[i][j]!=WALL_TILE and self.cover[i][j]==1:
                        return 0
                    
        return 1
            
class ALARM():
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.SURFACE=SURFACE
        
        #alarm
        self.Gamerule=1
        self.Gameclear=0
        self.Gameover_flag=0
        
        #game clear
        ## retry button
        self.re_b_size=(100,50)
        self.re_b_image=pygame.image.load("./minesweeper/re.png").convert_alpha()
        self.re_b_image=pygame.transform.scale(self.re_b_image,self.re_b_size)
        self.re_b_Rect=self.re_b_image.get_rect()
        self.re_b_image_mask=pygame.mask.from_surface(self.re_b_image)
        self.re_txt_size=25
        
        self.re_text_font = pygame.font.SysFont("arial", self.re_txt_size, True, False)
        self.re_text=\
        """
        오른쪽 위 빨간색 숫자는 쓰레기의 개수, \n
        왼쪽 아래 파란색 숫자는 아이템의 개수 \n
        아이템은 쓰레기를 탐지하는 아이템(탐지기)과 목숨을 채워주는 아이템(꽃) 중 하나\n
        지뢰와 아이템을 제외한 모든 땅을 열면 게임 클리어!\n
        마우스 우클릭 : 깃발 설치\n
        마우스 좌클릭 : 깃발 파괴, 타일 열기\n
        탐지기 아이템은 밑에 아이템을 누르면 탐지 가능 범위가 노란색으로 뜸\n
        그 이후 좌클릭을 하면 노란색 범위 안에 있는 지뢰에 깃발을 세움. \n
        """
        
        ##blurred effect
        self.blurred_effect_size=(width,height)
        self.blurred_effect_image=pygame.image.load("./minesweeper/background_blurred_effect.png").convert_alpha()
        self.blurred_effect_image=pygame.transform.scale(self.blurred_effect_image,self.blurred_effect_size)
        self.blurred_effect_image.set_alpha(230)
        self.blurred_effect_Rect=self.blurred_effect_image.get_rect()
        self.blurred_effect_image_mask=pygame.mask.from_surface(self.blurred_effect_image)
        
        
        #close button
        self.closebutton_size=(50,50)
        self.closebutton_image=pygame.image.load("./minesweeper/closebutton.png").convert_alpha()
        self.closebutton_image=pygame.transform.scale(self.closebutton_image,self.closebutton_size)
        self.closebutton_Rect=self.closebutton_image.get_rect()
        self.closebutton_image_mask=pygame.mask.from_surface(self.closebutton_image)
        self.txt_size=15
        
        self.text_font = pygame.font.SysFont("malgungothic", self.txt_size, True, False)
        self.text=\
        """
        오른쪽 위 빨간색 숫자는 쓰레기의 개수, \n\n
        왼쪽 아래 파란색 숫자는 아이템의 개수 \n\n
        아이템은 쓰레기를 탐지하는 아이템(탐지기)과 목숨을 채워주는 아이템(꽃) 중 하나\n\n
        지뢰와 아이템을 제외한 모든 땅을 열면 게임 클리어!\n\n
        마우스 우클릭 : 깃발 설치\n\n
        마우스 좌클릭 : 깃발 파괴, 타일 열기\n\n
        탐지기 아이템은 밑에 아이템을 누르면 탐지 가능 범위가 노란색으로 뜸\n\n
        그 이후 좌클릭을 하면 노란색 범위 안에 있는 지뢰에 깃발을 세움. \n\n
        """
        
    def retry_button(self):
        self.re_b_Rect=(450-self.re_b_size[0]/2, 695)
        self.SURFACE.blit(self.re_b_image,self.re_b_Rect)
        
    def blurred_effect(self):
        self.re_b_Rect=(0,0)
        self.SURFACE.blit(self.blurred_effect_image,self.blurred_effect_Rect)
        
    def close_button(self):
        self.closebutton_Rect.center=(776, 125)
        self.SURFACE.blit(self.closebutton_image,self.closebutton_Rect)
        
    def close_button_click(self):
        self.Gamerule=0

        
    def gamerule(self):
        pygame.draw.rect(self.SURFACE,color["whitegray"],[100,100,width-200,height-200])
        self.close_button()
        stack=self.text.split("\n")
        for i in range(len(stack)):
            text_Title=self.text_font.render(stack[i], True, color["black"])
            Rect=text_Title.get_rect()
            Rect.x=100
            Rect.y=100+self.closebutton_size[1]+10 + self.txt_size*i
            self.SURFACE.blit(text_Title, Rect)
 
    def gameclear(self,heart,item,time): # time 은 남은 시간
        self.blurred_effect()
        pygame.draw.rect(self.SURFACE,color["whitegray"],[300,300,width-600,height-600])
        if self.Gameclear==1:
            self.re_text=f"game clear!!\nscore is {int(max(10000,heart*time*500)+self.Gameover_flag*100+item*300)}"
        elif self.Gameclear==2:
            self.re_text=f"game over..\nscore is {int(self.Gameover_flag*100+item*300)}"
        self.retry_button()
        stack=self.re_text.split("\n")
        for i in range(len(stack)):
            text_Title=self.re_text_font.render(stack[i], True, color["black"])
            Rect=text_Title.get_rect()
            Rect.x=300+10
            Rect.y=300+self.re_b_size[1]+10 + self.re_txt_size*i
            self.SURFACE.blit(text_Title, Rect)
 
class MousePointer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.SURFACE=SURFACE
        self.pos=(0,0)
        self.mousepointer_size=(15,15)
        self.mousepointer_image=pygame.image.load("./minesweeper/mousepointer.png").convert_alpha()
        self.mousepointer_image.set_alpha(128)
        self.mousepointer_image=pygame.transform.scale(self.mousepointer_image,self.mousepointer_size)
        self.mousepointer_Rect=self.mousepointer_image.get_rect()
        self.mousepointer_image_mask=pygame.mask.from_surface(self.mousepointer_image)
        
    def draw(self,pos):
        self.mousepointer_Rect.center=pos
        self.SURFACE.blit(self.mousepointer_image,self.mousepointer_Rect)
 
class Item(pygame.sprite.Sprite):
    def __init__(self,tile_size,map_size,map_pos,MOD):
        pygame.sprite.Sprite.__init__(self)
        self.SURFACE=SURFACE
        self.pos=(0,0)
        self.mode=MOD
        self.map_pos=map_pos
        self.map_size=map_size
        self.item_size=tile_size
        self.item_radius=self.mode[4]#(1,1) # 좌우,위아래
        self.item_image=pygame.image.load("./minesweeper/item.png").convert_alpha()
        #self.mousepointer_image.set_alpha(128)
        self.item_image=pygame.transform.scale(self.item_image,self.item_size)
        self.item_image_mask=pygame.mask.from_surface(self.item_image)
        
    def draw(self,pos):
        #print("POS",pos)
        for y in range(-1*self.item_radius[1],1*self.item_radius[1]+1):
            for x in range(-1*self.item_radius[0],1*self.item_radius[0]+1):
                #print("next pos",(pos[0]+x,pos[1]+y))
                if 0<=pos[0]+x<self.map_size[0] and 0<=pos[1]+y<self.map_size[1]:
                    self.SURFACE.blit(self.item_image,[self.map_pos[0]+(pos[0]+x)*self.item_size[0],self.map_pos[1]+(pos[1]+y)*self.item_size[1]])
        
     
class Virtual_Object(pygame.sprite.Sprite):
    def __init__(self,object): #object = [image, rect, mask]
        pygame.sprite.Sprite.__init__(self)
        self.image=object[0]
        self.rect=object[1]
        self.mask=object[2]
        self.radius=0
     
            
def GAME(mod=1):
    MODE=mode[mod]
    game=GAMESYSTEM(MODE)
    alarm=ALARM()
    mousepointer=MousePointer()
    item=Item(game.tile_size,game.map_size,game.map_pos,MODE)

    #developer=True

    while 1:
        SURFACE.fill(color["white"])
        for EVENT in pygame.event.get():
            if EVENT.type==QUIT:pygame.quit();sys.exit()
            if EVENT.type==MOUSEBUTTONDOWN: #if pygame.mouse.get_pressed()[0]: #0 : 왼, 1 : 휠, 2 : 오
                
                #if developer:
                
                if alarm.Gamerule==0 and not game.item_using and alarm.Gameclear==0:
                    if pygame.mouse.get_pressed()[0]:
                        POS=game.click_pos(pygame.mouse.get_pos())
                        #print(pygame.mouse.get_pos(),POS)
                        game.cover_off(POS)
                    elif pygame.mouse.get_pressed()[2]:
                        POS=game.click_pos(pygame.mouse.get_pos())
                        game.flag_on(POS)
                    
                else:
                    A=Virtual_Object([mousepointer.mousepointer_image,mousepointer.mousepointer_Rect,mousepointer.mousepointer_image_mask])
                    
                    if alarm.Gamerule==1:
                        B=Virtual_Object([alarm.closebutton_image,alarm.closebutton_Rect,alarm.closebutton_image_mask])
                        
                        if pygame.mouse.get_pressed()[0] and pygame.sprite.collide_mask(A,B):
                            alarm.Gamerule=0
                            game.game_start()
                            
                    elif alarm.Gameclear!=0:
                        if pygame.mouse.get_pressed()[0]:
                            POS=game.click_pos(pygame.mouse.get_pos())
                            #print(pygame.mouse.get_pos(),POS)
                        B=Virtual_Object([alarm.re_b_image,alarm.re_b_Rect,alarm.re_b_image_mask])
                        
                        if pygame.mouse.get_pressed()[0] and pygame.sprite.collide_mask(A,B):
                            alarm.Gameclear=0
                            #print("!@!@!@!@!@")
                            print("!@#!@#")
                            return
                    
            
        if game.start:
        
            
            game.item_use(Virtual_Object([mousepointer.mousepointer_image,mousepointer.mousepointer_Rect,mousepointer.mousepointer_image_mask]))
            game.draw(alarm.Gameclear)
            
            if game.item_using:
                POS=game.click_pos(pygame.mouse.get_pos())
                if 0<=POS[0]<game.map_size[0] and 0<=POS[1]<game.map_size[1]:
                    item.draw(POS)
                if pygame.mouse.get_pressed()[0]:
                    POS=game.click_pos(pygame.mouse.get_pos())
                    if 0<=POS[0]<game.map_size[0] and 0<=POS[1]<game.map_size[1]:
                        game.detect(POS,item.item_radius)
                        game.item_using=False
                
            
            if alarm.Gameclear==0:
                
                if game.Time<=0:
                    game.finish=2
                    
                if game.clear_condition():
                    game.finish=1
                
            if game.finish>0:
                if game.finish==1:
                    print("game clear")
                    alarm.Gameover_flag=game.check_flag()
                    alarm.Gameclear=1
                    game.finish_time=game.Time
                elif game.finish==2:
                    print("game over")
                    alarm.Gameover_flag=game.check_flag()
                    alarm.Gameclear=2
                    game.finish_time=game.Time
                #sys.exit()
                game.finish=0

        if alarm.Gamerule:
            alarm.gamerule()
            
        if alarm.Gameclear:
            alarm.gameclear(game.heart,game.item_cnt,game.finish_time)
            
            
        mousepointer.draw(pygame.mouse.get_pos())
            
        pygame.display.update()
        
level=3
while 1:
    GAME(level)

        