#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os, sys
from random import randint, choice
from math import sin, cos, radians
from datetime import datetime

import pygame
from pygame.locals import *
from pygame.sprite import Sprite

from vec2d import vec2d
from simpleanimation import SimpleAnimation


class Creep(Sprite):
    """ A creep sprite that bounces off walls and changes its
        direction from time to time.
    """
    def __init__(   
            self, screen, creep_image,init_position,
            init_direction, speed, **kv):
        """ Create a new Creep.
        
            screen: 
                The screen on which the creep lives (must be a 
                pygame Surface object, such as pygame.display)
            
            creep_image: 
                Image (surface) object for the creep
            
            field:
                A Rect specifying the 'playing field' boundaries.
                The Creep will bounce off the 'walls' of this 
                field.
                
            init_position:
                A vec2d or a pair specifying the initial position
                of the creep on the screen.
            
            init_direction:
                A vec2d or a pair specifying the initial direction
                of the creep. Must have an angle that is a 
                multiple of 45 degres.
            
            speed: 
                Creep speed, in pixels/millisecond (px/ms)

            **kw:
                passing parameters
        """
        Sprite.__init__(self)
        
        self.screen = screen
        self.speed = speed
        self.field = screen.get_rect()
        
        # base_image holds the original image, positioned to
        # angle 0.
        # image will be rotated.
        #
        self.base_image = creep_image
        self.image = self.base_image
        self.image_w, self.image_h = self.image.get_size()
        # A vector specifying the creep's position on the screen
        #
        self.pos = vec2d(init_position)

        # The direction is a normalized vector
        #
        self.direction = vec2d(init_direction).normalized()
        # 
        self.exploding = 0
        #
        for k,v in kv.items():
            self.__dict__[k] = v

            
    def update(self, time_passed):
        """ Update the creep.
        
            time_passed:
                The time passed (in ms) since the previous update.
        """
        if not self.exploding:
            # Maybe it's time to change the direction ?
            #
            self._change_direction(time_passed)
            
            # Make the creep point in the correct direction.
            # Since our direction vector is in screen coordinates 
            # (i.e. right bottom is 1, 1), and rotate() rotates 
            # counter-clockwise, the angle must be inverted to 
            # work correctly.
            #
            self.image = pygame.transform.rotate(
                self.base_image, -self.direction.angle)
            
            # Compute and apply the displacement to the position 
            # vector. The displacement is a vector, having the angle
            # of self.direction (which is normalized to not affect
            # the magnitude of the displacement)
            #
            displacement = vec2d(    
                self.direction.x * self.speed * time_passed,
                self.direction.y * self.speed * time_passed)
            
            self.pos += displacement
            
            # When the image is rotated, its size is changed.
            # We must take the size into account for detecting 
            # collisions with the walls.
            #
            bounds_rect = self.field.inflate(-self.image_w, -self.image_h)

            if self.pos.x < bounds_rect.left:
                self.pos.x = bounds_rect.left
                self.direction.x *= -1
            elif self.pos.x > bounds_rect.right:
                self.pos.x = bounds_rect.right
                self.direction.x *= -1
            elif self.pos.y < bounds_rect.top:
                self.pos.y = bounds_rect.top
                self.direction.y *= -1
            elif self.pos.y > bounds_rect.bottom:
                self.pos.y = bounds_rect.bottom
                self.direction.y *= -1
        else:
            self.bang.update(time_passed)
            self.kill()

    def draw(self):
        """ Blit the creep onto the screen that was provided in
            the constructor.
        """
        if not self.exploding:
            # The creep image is placed at self.pos.
            # To allow for smooth movement even when the creep rotates
            # and the image size changes, its placement is always
            # centered.
            #
            draw_pos = self.image.get_rect().move(
                self.pos.x - self.image_w / 2, 
                self.pos.y - self.image_h / 2)
            self.screen.blit(self.image, draw_pos)
        else:
            self.bang.draw()
    
    def Collision(self, pos):
        """ The mouse was clicked in pos.
        """
        if self._point_is_inside(pos):
            # self.kill()
            # self._explode()
            return True

    def _point_is_inside(self, point):
        """ Is the point (given as a vec2d) inside our creep's
            body?
        """
        img_point = point - vec2d(  
            int(self.pos.x - self.image_w / 2),
            int(self.pos.y - self.image_h / 2))
        try:
            pix = self.image.get_at(img_point)
            return pix[3] > 0
        except IndexError:
            return False
    #------------------ PRIVATE PARTS ------------------#
    
    # States the creep can be in.
    #
    # ALIVE: The creep is roaming around the screen
    # EXPLODING: 
    #   The creep is now exploding, just a moment before dying.
    # DEAD: The creep is dead and inactive
    #
    (ALIVE, EXPLODING, DEAD) = range(3)    

    _counter = 0
    def _change_direction(self, time_passed):
        """ Turn by 45 degrees in a random direction once per
            0.4 to 0.5 seconds.
        """
        self._counter += time_passed
        if self._counter > randint(700, 3000):
            self.direction.rotate(45 * randint(-1, 1)) # collision
            self._counter = 0

    def _explode(self):
        """ Starts the explosion animation that ends the Creep's
            life.
        """
        self.exploding = 1
        pos = ( self.pos.x - self.explosion_images[0].get_width() / 2,
                self.pos.y - self.explosion_images[0].get_height() / 2)
        self.bang = SimpleAnimation(self.screen, pos, self.explosion_images,10000)



class Dodgeball(Creep):
    def update(self,move):
        if not self.exploding:
            # move control
            self.pos.x -= move[K_LEFT]
            self.pos.x += move[K_RIGHT]
            self.pos.y -= move[K_UP]
            self.pos.y += move[K_DOWN]
            # collisions with the walls
            self.image_w, self.image_h = self.image.get_size()
            bounds_rect = self.field.inflate( -self.image_w, -self.image_h)
            if self.pos.x < bounds_rect.left:
                self.pos.x = bounds_rect.left
            elif self.pos.x > bounds_rect.right:
                self.pos.x = bounds_rect.right
            elif self.pos.y < bounds_rect.top:
                self.pos.y = bounds_rect.top
            elif self.pos.y > bounds_rect.bottom:
                self.pos.y = bounds_rect.bottom
        else:
            self.bang.update()
            self.kill()




class Game(object):
    # Game parameters
    SCREEN_WIDTH, SCREEN_HEIGHT = (920, 620)
    FIELD_WIDTH = SCREEN_WIDTH
    FIELD_HEIGHT = 540
    MESSAGE_WIDTH,MESSAGE_HEIGHT = SCREEN_WIDTH,SCREEN_HEIGHT-FIELD_HEIGHT
    BG_COLOR = (251, 251, 251)
    FONT_COLOR = (250, 250, 250)
    CREEP_FILENAMES = [
        'data/xx.png',
        'data/circle.png', 
        'data/triangle.png', 
        'data/square.png']
    # CREEP_FILENAMES = [
    #     'data/16.png']
    N_CREEPS = 70
    # Game state  ove:-1 reload:0  playing:1
    STATE = 0

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("是XX就坚持XX秒!  (￣ε(#￣)")
        # Surface init
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 1 , 32)
        self.game_field = pygame.Surface((self.FIELD_WIDTH,self.FIELD_HEIGHT))
        self.message_board = pygame.Surface((self.MESSAGE_WIDTH,self.MESSAGE_HEIGHT)) 
        # text font
        self.font = pygame.font.Font('data/Font.ttf',23)
        # images
        self.icon = pygame.image.load('data/icon.png').convert_alpha()
        self.bg_title_img = pygame.image.load('data/bg.gif').convert_alpha()
        self.explosion_img = pygame.image.load('data/explosion1.png').convert_alpha()
        self.move_img = pygame.image.load('data/move.png').convert_alpha()
        self.creep_images = [pygame.image.load(filename).convert_alpha() for filename in self.CREEP_FILENAMES]
        self.explosion_images = [pygame.transform.rotate(self.explosion_img,angle) for angle in range(0,360, 180)]
        # set icon
        pygame.display.set_icon(self.icon)
        # music
        pygame.mixer.music.load('data/creep.mp3')
        # keyboard
        pygame.key.set_repeat()
        # set time
        self.clock = pygame.time.Clock()
        # music
        pygame.mixer.music.play(-1)


    def load_game(self):
        self.paused = False
        self.move = {K_UP:0, K_DOWN:0, K_LEFT:0, K_RIGHT:0}
        # Create N_CREEPS random creeps.
        self.creeps = pygame.sprite.Group()    
        for i in range(self.N_CREEPS):
            self.creeps.add(
                Creep(
                    screen=self.game_field,
                    creep_image=choice(self.creep_images),
                    init_position=( randint(5,self.FIELD_WIDTH-5),
                                    randint(5,self.FIELD_HEIGHT-5)),
                    init_direction=(choice([-1,1]),
                                    choice([-1,1])),
                    speed=0.1
                    )
                )
        self.ball_pos = (10,10)   
        self.dodgeball= Dodgeball(self.game_field, self.move_img, self.ball_pos, (10,7), 5,explosion_images=self.explosion_images)
        self.start_time = 0
        self.passed_time = 0


    def run(self):
        self.load_game()
        while 1:
            # Limit frame speed to 50 FPS
            self.time_passed = self.clock.tick(50)
            self.FPS = int(1000./self.time_passed)
            # keyboard event 
            for event in pygame.event.get():
                # quit
                if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.exit_game()
                # ready to game
                if self.STATE == 0:
                    # start game
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.STATE = 1
                        pygame.mouse.set_visible(False)
                        self.start_time = pygame.time.get_ticks()
                    if pygame.mouse.get_pressed()[0]:
                        self.dodgeball.pos.x, self.dodgeball.pos.y = pygame.mouse.get_pos()
                # playing
                if self.STATE == 1:
                    # pause game    
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.paused = not self.paused
                        if self.paused:
                            self.break_point = pygame.time.get_ticks()
                        else:
                            self.passed_time += pygame.time.get_ticks() - self.break_point
                    # contrl move
                    if event.type == pygame.KEYDOWN:
                        if event.key in self.move:
                            self.move[event.key] = self.dodgeball.speed # ball speed
                    if event.type == KEYUP:
                        if event.key in self.move:
                            self.move[event.key] = 0
                # game over
                if self.STATE == -1:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.STATE = 0
                        self.paused = not self.paused
                        pygame.mouse.set_visible(True)
                        self.load_game()

            # main
            if self.STATE == 0:
                self.draw_background()
                self.message_board.blit(self.font.render(u'用鼠标点击选择初始位置,方向键控制方向，「p」键暂停，「ESC」键退出。',True,self.FONT_COLOR),(27,10))
                self.message_board.blit(self.font.render(u'「回车键」开始游戏 ',True,self.FONT_COLOR),(27,40))
                for creep in self.creeps:
                    creep.draw()
                self.dodgeball.draw()
                self.screen_update()


            if self.STATE == 1 and not self.paused:
                #
                self.draw_background()
                self.draw_message()
                #
                # elements
                self.element_move()
                self.screen_update()

            if self.STATE == -1:
                self.game_field.fill(self.BG_COLOR)
                for creep in self.creeps:
                    creep.draw()
                self.dodgeball.update(self.time_passed)
                self.dodgeball.draw()
                self.screen_update()

            pygame.display.flip()

    def draw_background(self):
        # Redraw the background
        self.game_field.fill(self.BG_COLOR)
        self.tile_pic(self.message_board,self.bg_title_img)

    def draw_message(self):
        self.message_board.blit(self.font.render(u'Time: %.2fs' %self.get_play_time(),True,self.FONT_COLOR),(47,10))

    def element_move(self):
        self.dodgeball.update(self.move)
        self.dodgeball.draw()
        # Update and redraw all creeps
        for creep in self.creeps:
            creep.update(self.time_passed)
            creep.draw()
            creep.speed = 0.1 + int(self.get_play_time())/10*0.02
            if creep.Collision(self.dodgeball.pos):
                self.dodgeball._explode()
                # game over
                self.game_over()

                
    def screen_update(self):
        # clock
        self.screen.blit(self.game_field,(0,0))
        self.screen.blit(self.message_board,(0,self.FIELD_HEIGHT))

    def get_play_time(self):
        t = pygame.time.get_ticks() - self.start_time - self.passed_time
        return t/1000. 

    def tile_pic(self,surface,image):
        width,height = surface.get_size()
        img_w,img_h  = image.get_size()
        for y in range(0,height,img_h):
            for x in range(0,width,img_w):
                surface.blit(image,(x,y))

    def game_over(self):
        self.STATE = -1
        self.paused = not self.paused
        self.message_board.blit(self.font.render(u'「回车键」重新开始游戏',True,self.FONT_COLOR),(27,40))
        self.message_board.blit(self.font.render(u'GAME OVER  ┑(￣。￣)┍',True,(255,0,0)),(300,10))
        
    def exit_game(self):
        pygame.display.quit()
        sys.exit()

        

if __name__ == '__main__':
    game = Game()
    game.run()
