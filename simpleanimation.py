import sys
import pygame


class SimpleAnimation(object):
    """ A simple animation. Scrolls cyclically through a list of
        images, drawing them onto the screen in the same posision.    
    """
    def __init__(self, screen, pos, images, scroll_period, duration=-1):
        """ Create an animation.        
            
            screen: The screen to which the animation will be drawn
            pos: Position on the screen
            images: 
                A list of surface objects to cyclically scroll through
            scroll_period: 
                Scrolling period (in ms)
            duration:
                Duration of the animation (in ms). If -1, the 
                animation will have indefinite duration.
        """
        self.screen = screen
        self.images = images
        self.pos = pos
        self.scroll_period = scroll_period
        self.duration = duration
        self.time_passed = float(scroll_period)/len(images)
        self.img_ptr = 0
        self.duration_count = 0
        self.scroll_count = 0
        self.active = True
    
    def is_active(self):
        """ Is the animation active ?
        
            An animation is active from the moment of its creation
            and until the duration has passed.
        """
        return self.active
    
    def update(self):
        """ Update the animation's state.
        
            time_passed:
                The time passed (in ms) since the previous update.
        """
        self.scroll_count += self.time_passed
        if self.scroll_count > self.scroll_period:
            self.scroll_count -= self.scroll_period
            self.img_ptr = (self.img_ptr + 1) % len(self.images)
        
        if self.duration >= 0:
            self.duration_count += self.time_passed
            if self.duration_count > self.duration:
                self.active = False

    def draw(self):
        """ Draw the animation onto the screen.
        """
        if self.active:
            cur_img = self.images[self.img_ptr]
            x,y = self.pos
            pos = x-cur_img.get_width()/2,y-cur_img.get_height()/2
            self.draw_rect = cur_img.get_rect().move(pos)
            self.screen.blit(cur_img, self.draw_rect)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((300, 300), 0, 32)

    clock = pygame.time.Clock()
    explosion_img = pygame.image.load('data/explosion1.png').convert_alpha()
    images = [explosion_img, pygame.transform.rotate(explosion_img, 90)]
    images = [ pygame.transform.rotate(explosion_img, -angle) for angle in range(0,360,10)]
    print len(images)
    expl = SimpleAnimation(screen, (100, 100), images, 1, -1)

    while True:
        time_passed = clock.tick(50)
        
        screen.fill((0, 0, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        expl.update(time_passed)
        expl.draw()
        
        pygame.display.flip()

