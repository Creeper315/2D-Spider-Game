import pygame as py
import helper
import spider
from pygame.draw import circle as cir
from pygame.draw import line
from pygame.draw import rect

color_lgreen = (237, 250, 217)    # light green
color_black = (36, 33, 29)
color_blue = (57, 127, 247)
color_orange = (247, 165, 32)
screen = py.display.set_mode((800, 800))
py.display.set_caption('a spider')
list_obstacle = []
print('Screen Size : '+ str(screen.get_size()))

C = py.time.Clock()


def main():
    #bk_img2 = p.transform.chop(bk_img, (10, 40, 40, 10))
    bk = py.Surface((1, 1))
    bk.fill(color_blue)
    g = spider.Game()
    s = spider.Spider()
    s.rect = cir(screen, color_orange, (round(s.x), round(s.y)), s.size)

    r6 = rect(screen, color_lgreen, (screen.get_size()[0] - 10, 200, 10, 200))
    r4 = rect(screen, color_lgreen, (50, 50, 50, 50))
    r5 = rect(screen, color_lgreen, (280, 65, 40, 10))
    r1 = rect(screen, color_lgreen, (298, 550, 50, 50))
    r2 = rect(screen, color_lgreen, (500, 500, 100, 100))
    r3 = rect(screen, color_lgreen, (60, 380, 100, 50))

    list_obstacle = [r1,r2,r3,r4,r5,r6]
    list_obstacle.append(rect(screen, color_lgreen, (500, 100, 150, 40)))
    list_obstacle.append(rect(screen, color_lgreen, (670, 430, 50, 50)))
    list_obstacle.append(rect(screen, color_lgreen, (0, screen.get_size()[1]-10, screen.get_size()[0], 10)))

    while True:     # Animation loop
        C.tick(g.fps)
        #print(s.x, s.y)
        #if g.queue[-1] == 'right'
        if s.y > screen.get_size()[1]:# or s.x < 0.7*screen.get_size()[0] or s.x > 1.7*screen.get_size()[0]:
            s.x = 125
            s.y = 100
            s.x_speed = 1
            s.y_speed = 3
        for event in py.event.get():
            helper.event_helper(event, g)

        helper.draw_image(bk, screen=screen)
        helper.mouse_click(s)
        #print(s.x_spring_speed, s.y_spring_speed)
        #print('~~~~'+str(s.y_speed))
        helper.handle_spider(s, g, list_obstacle)
        #print(s.y_speed)
        helper.handle_spring(s, list_obstacle)

        helper.draw_spring(s, color_black, screen)
        helper.draw_all_obs(list_obstacle, color_lgreen, screen)
        helper.draw_spider(s, color_orange, screen)
        #print(s.x, s.y, s.x_speed, s.y_speed)


        py.display.update()

if __name__ == '__main__':
    main()
    # remember to run Main function


