

class Game:
    def __init__(self):
        self.fps = 50
        self.gravity = 1
        self.mouse_clicked = False

        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.queue = []

        self.game_on = False
        #self.collided_in_previous_frame = False

class Spider:
    def __init__(self):
        self.rect = None
        self.size = 20   # Maybe this is the radius of spider
        self.mass = 10
        self.f_movement = 5   # Force,    F = m / a —————— so , a = m / F
        self.s_shoot = 57
        self.stiffness_spring = 0.02

        self.x = 215
        self.y = 100
        self.x_speed = -1
        self.y_speed = 3


        self.spring_unreleased = True
        self.spring_out = False
        self.spring_width = 2
        self.x_spring = self.x
        self.y_spring = self.y
        self.x_spring_speed = 0
        self.y_spring_speed = 0
        self.spring_attached = False
        self.spring_back = False    # is spring going back towards the spider ?

        self.spider_bounciness = 0.83 # The higher value makes the spider more bouncy when collide with objects.
        self.spider_friction = 0.1
        self.on_surface = False # if the distance between spider & obstacle is smaller or equal to spider (size + 1), we say spider is on the surface of an obstacle


class Obstacle:
    def __init__(self):
        pass

