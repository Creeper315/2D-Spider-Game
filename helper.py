import pygame as py
import sys
from pygame.locals import *
import math
import numpy as np

def draw_image(img, a = None, b = None, screen = None):
    # a and b are both 4 element Tuples !  a is where to cut from img, b is where to draw on screen
    # a's X and Y are both from 0 ~ 100, it is how many percent, say we cut img with width from 15% length to 60% length, it would be (15, ... , 60, ...)
    # if a is not specified, we will not cut part of the image, we would use the full image.
    # if b is not specified, we'll draw img and cover the entire screen
    if screen == None:
        raise ('screen cannot be None')
    if a == None:
        a = (0,0,100,100)
    if b == None:
        b = (0,screen.get_size()[1])+screen.get_size()   # is b is not specified, we will draw image to cover entire screen.
    i_size = img.get_size()
    h_scale = i_size[0] / 100
    v_scale = i_size[1] / 100

    a = (a[0]*h_scale, a[1]*v_scale, a[2]*h_scale, a[3]*v_scale)

    h_scale = b[2] / a[2]
    v_scale = b[3] / a[3]
    img = py.transform.flip(img, (h_scale < 0), (v_scale < 0))
    h_scale = abs(h_scale)
    v_scale = abs(v_scale)
    img = py.transform.scale(img, (round(i_size[0]*h_scale), round(i_size[1]*v_scale)))
    a = (a[0]*h_scale, a[1]*v_scale, a[2]*h_scale, a[3]*v_scale)
    i = 0
    j = 0
    if b[2] < 0:
        i = b[2]
    if b[3] > 0:
        j = b[3]
    screen.blit(img, (b[0]+i,b[1]-j), a)

def detect_circle_collision(s, obs):
    sx = s.x
    sy = s.y
    ss = s.size
    def f(a,b,c,d):
        return a,b,c,d
    x, y, w, h = f(*obs)
    if sx+ss < x or sx-ss > x+w or sy+ss < y or sy-ss > y+h:
        return False
    if sx<x and sy<y and math.hypot(sx-x, sy-y) > ss:
        return False
    elif sx<x and sy>y+h and math.hypot(sx-x, sy-(y+h)) > ss:
        return False
    elif sx>x+w and sy<y and math.hypot(sx-(x+w), sy-y) > ss:
         return False
    elif sx > x+w and sy > y+h and math.hypot(sx-(x+w), sy-(y+h)) > ss:
        return False
    else:
        return True

def queue_helper(key_name, queue, insert):
    if insert:
        if len(queue) == 0 or queue[0] is not key_name:
            queue.insert(0, key_name)
            if len(queue) > 2:
                queue.pop()
    else:
        try:
            queue.remove(key_name)
        except:
            pass

def event_helper(e, g):
    if e.type == QUIT:
        py.quit()
        sys.exit()
    elif e.type == KEYDOWN:
        if e.key == K_UP:
            g.up = True
        elif e.key == K_DOWN:
            g.down = True
        elif e.key == K_LEFT:
            g.left = True
            queue_helper('left', g.queue, True)
        elif e.key == K_RIGHT:
            g.right = True
            queue_helper('right', g.queue, True)

    elif e.type == KEYUP:
        if e.key == K_UP:
            g.up = False
            if g.fps <= 50:
                g.fps += 10
            elif g.fps < 60:
                g.fps = 60
        elif e.key == K_DOWN:
            g.down = False
            if g.fps >= 12:
                g.fps -= 7
            elif g.fps >5:
                g.fps = 5
            elif g.fps == 5:
                g.fps = 2
            else:
                g.fps = 1
        elif e.key == K_LEFT:
            g.left = False
            queue_helper('left', g.queue, False)
        elif e.key == K_RIGHT:
            g.right = False
            queue_helper('right', g.queue, False)

def get_tengential_component(s_x, s_y, x, y, length=None):
    # Returns the x, y axis components of the vector, this vector goes from (s_x, s_y) to direction (x, y) and has length = length.
    if x - s_x == 0 and y - s_y == 0:
        print('what the heck ?')
        return 0, 0
    if length == None:
        length = math.hypot(x - s_x, y - s_y)
    if x - s_x == 0:
        return 0, (length * int(float(np.sign(y - s_y))))
    if y - s_y == 0:
        return (length * int(float(np.sign(x - s_x)))), 0
    slope = (y - s_y) / (x - s_x)
    a = math.sqrt(length**2 / (1+slope**2))
    b = a * slope
    a *= (x - s_x) / abs(x - s_x)
    b = abs(b) * ((y - s_y) / abs(y - s_y))
    return a, b # Keep in mind, the coordinate of pygame, y is flipped. y increases as we go downwards

def calculate_spring_tension(s): # the force from tip of spring to spider
    dist = math.hypot(s.x_spring - s.x, s.y_spring - s.y)
    force = s.stiffness_spring * dist
    force = float(force)
    return get_tengential_component(s.x_spring, s.y_spring, s.x, s.y, force)

def mouse_click(s):
    if py.mouse.get_pressed()[0] and s.spring_unreleased:
        s.spring_out = True
        s.spring_unreleased = False
        x = py.mouse.get_pos()[0]
        y = py.mouse.get_pos()[1]

        a, b = get_tengential_component(s.x, s.y, x, y, s.size)
        s.x_spring = s.x + a
        s.y_spring = s.y + b

        a, b = get_tengential_component(s.x, s.y, x, y, s.s_shoot)
        s.x_spring_speed = a
        s.y_spring_speed = b

    if not py.mouse.get_pressed()[0] and s.spring_attached:
        s.spring_attached = False
        s.spring_out = False
        s.spring_back = True
        s.x_spring_speed = 0
        s.y_spring_speed = 0

def set_spring_x_y_if_collide_with_rect(s, x_prev, y_prev, obs):
    # It return True if the spring collide with rectangle 'obs', at the same time, set (x,y) pos of tip of spring
    def f2(s):
        s.spring_attached = True
        s.spring_out = False
        s.x_spring_speed = 0
        s.x_spring_speed = 0
    def f(a,b,c,d):
        return a,b,c,d
    x, y, w, h = f(*obs)
    print('~~~')
    print(x_prev, y_prev)
    print(x,y,w,h)

    x -= x_prev
    y -= y_prev
    sx = s.x_spring - x_prev
    sy = s.y_spring - y_prev
    slope = sy / sx
    slope2 = sx / sy
    if x > 0:
        yy = x * slope
        if sx >= x and yy > y and yy < y+h:
            s.x_spring = x_prev + x
            s.y_spring = y_prev + yy
            f2(s)
            return True
    if y > 0:
        xx =  y * slope2
        if sy >= y and xx > x and xx < x+w:
            s.x_spring = x_prev + xx
            s.y_spring = y_prev + y
            f2(s)
            return True
    if x+w < 0:
        yy = (x+w) * slope
        if sx <= x+w and yy > y and yy < y+h:
            s.x_spring = x_prev + x+w
            s.y_spring = y_prev + yy
            f2(s)
            return True
    if y+h < 0:
        xx = (y+h) * slope2
        if sy<=y+h and xx > x and xx < x+w:
            s.x_spring = x_prev + xx
            s.y_spring = y_prev + y+h
            f2(s)
            return True
    return False

def handle_spring(s, list_obstacle):
    if s.spring_unreleased or s.spring_attached:
        return
    if s.spring_out:
        sx_previous = s.x_spring
        sy_previous = s.y_spring
        x_previous_speed = s.x_spring_speed
        y_previous_speed = s.y_spring_speed

        s.x_spring += x_previous_speed
        s.y_spring += y_previous_speed
        a, b = calculate_spring_tension(s)
        s.x_spring_speed += a
        s.y_spring_speed += b
        if s.x_spring_speed * x_previous_speed <= 0 or s.y_spring_speed * y_previous_speed <= 0:
            s.spring_out = False
            s.spring_back = True

        for o in list_obstacle:
            if set_spring_x_y_if_collide_with_rect(s, sx_previous, sy_previous, o):
                break

    if s.spring_back:
        x_acc, y_acc = calculate_spring_tension(s)
        s.x_spring_speed += x_acc
        s.y_spring_speed += y_acc
        a = s.x_spring - s.x
        b = s.y_spring - s.y
        s.x_spring += s.x_spring_speed
        s.y_spring += s.y_spring_speed

        if a * (s.x_spring - s.x) <= 0 or b * (s.y_spring - s.y) <= 0:
            s.spring_unreleased = True
            s.spring_back = False

def handle_spider(s, g, list_obs):

    if not s.spring_attached:
        acceleration = g.gravity / s.mass  # acceleration is downwards, so acceleration should be negative value
        s.y_speed += acceleration
        #handle_spider_on_surface(s)
        if s.on_surface:
            pass
            #print(s.x_speed, s.y_speed)
        s.y += s.y_speed
        s.x += s.x_speed

    elif s.spring_attached:
        a, b = calculate_spring_tension(s)
        b = -b + g.gravity
        a = -a
        s.x_speed += (a / s.mass)
        s.y_speed += (b / s.mass)
        #handle_spider_on_surface(s)
        s.x += s.x_speed
        s.y += s.y_speed
    s.rect[0] = s.x - s.size
    s.rect[1] = s.y - s.size
    for e in list_obs:
        if detect_circle_collision(s, e):
            #print('~~~~~')
            update_spider_speed_upon_collision(s, e)


def handle_spider_on_surface(s):

    if not s.on_surface:
        return
    if s.direction_of_contact_point == 'down' and s.y_speed > 0:# and s.y_speed < 1:
        s.y_speed = 0
    if s.direction_of_contact_point == 'right' and s.x_speed > 0:# and s.x_speed < 1:
        s.x_speed = 0
    if s.direction_of_contact_point == 'left' and s.x_speed < 0:# and s.x_speed > -1:
        s.x_speed = 0
    if s.direction_of_contact_point == 'up' and s.y_speed < 0:# and s.y_speed > -1:
        s.y_speed = 0

def update_spider_speed_upon_collision(s, obs):   # it returns x, y components of force applied to spider when spider collide with object

    sx, sy, x_contact, y_contact, x_next, y_next = calculate_point_of_contact(s, obs)
    s.x = sx
    s.y = sy
    update_x_y_speed_given_point_of_contact(s, x_contact, y_contact, x_next, y_next)


def calculate_point_of_contact(s, obs):
    # it returns the (x,y) point which spider collide with obstacle
    # also return the position of spider for contacting this collision point
    x_next = s.x
    y_next = s.y
    x_previous  = s.x - s.x_speed
    y_previous  = s.y - s.y_speed
    x_result = x_previous
    y_result = y_previous
    a, b = get_tengential_component(s.x, s.y, x_previous, y_previous)
    current_length = float(np.linalg.norm((a,b)))
    current_length = int(current_length+1)
    length_tracker = 0
    a, b = get_tengential_component(s.x, s.y, x_previous, y_previous, 1)

    while True:
        sx = s.x
        sy = s.y
        if current_length == 1: # Base Case !   , 0.5 is just a random number, just make sure current length is smaller than 1 to reach base case
            if current_length < 1:
                print ('what ?????')
            break

        k = int(current_length / 2) + length_tracker

        s.x += round(a * k)  # Minus aa or add aa ????????/
        s.y += round(b * k)

        if detect_circle_collision(s, obs):
            current_length = current_length - int(current_length / 2)
            length_tracker += int(current_length / 2)
        else:
            x_result = s.x
            y_result = s.y
            s.x = sx
            s.y = sy
            current_length = int(current_length / 2)

    def f(a,b,c,d):
        return a,b,c,d
    x, y, w, h = f(*obs)
    x_contact = None
    y_contact = None
    s.on_surface = True

    if x_result < x:
        if y_result < y:
            x_contact, y_contact = x, y
        elif y_result > y+h:
            x_contact, y_contact = x, y+h
        else:
            x_contact, y_contact = x, y_result
            #s.direction_of_contact_point = 'right'
            s.on_surface = True
    elif x_result > x+w:
        if y_result < y:
            x_contact, y_contact = x+w, y
        elif y_result > y+h:
            x_contact, y_contact = x+w, y+h
        else:
            x_contact, y_contact = x+w, y_result
            #s.direction_of_contact_point = 'left'
            s.on_surface = True

    elif y_result < y:
        x_contact, y_contact = x_result, y
        #s.direction_of_contact_point = 'down'
        s.on_surface = True

    else:
        x_contact, y_contact = x_result, y+h
        #s.direction_of_contact_point = 'up'
        s.on_surface = True

    #k = math.hypot(x_result-x_contact, y_result-y_contact)
    #print(s.size, k)

    return x_result, y_result, x_contact, y_contact, x_next, y_next


def update_x_y_speed_given_point_of_contact(s, x, y, x_next, y_next):  # input x and y are (x,y) coordinate where spider collide with object.
    sx = s.x
    sy = s.y
    ss = s.size
    a, b = get_tengential_component(sx, sy, x, y, ss)
    v1 = np.array([a, b])
    v2 = np.array([s.x_speed, s.y_speed])
    # Note, I think cos_speed is magnitude, not a vector
    cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    cos_speed = math.hypot(s.x_speed, s.y_speed) * cos_theta
    cos_speed = cos_speed * s.spider_bounciness
    cos_speed = float(cos_speed)
    #print('~~~~~~~~')
    a, b = get_tengential_component(x, y, sx, sy, cos_speed)
                            # cos1 is the first cosine vector component of speed
    cos1 = np.array([a, b])
    cos2 = v2 + cos1
    cos2 *= (1 - s.spider_friction)   # This is how friction affects spider's speed on x_axis
    #print('cos_θ is : '+ str(cos_theta))
    #print('cos2 is smaller than speed vector ? '+ str(np.linalg.norm(cos2) / np.linalg.norm(v2)))
    #print(v2, cos1, cos2, np.linalg.norm(v2))
    #print(np.linalg.norm(np.array([a,b]) - cos2) == np.linalg.norm(v2))
    #test1 = (s.x_speed, s.y_speed)
    s.x_speed = float(cos1[0] + cos2[0])
    s.y_speed = float(cos1[1] + cos2[1])
    if abs(s.x_speed) < 0.001:   # Friction makes speed smaller and smaller, but never reaches 0. speed can be 1.0×e-10, but still not zero
        s.x_speed = 0
    if abs(s.y_speed) < 0.001:
        s.y_speed = 0
    #print(np.linalg.norm((s.x_speed, s.y_speed)) / np.linalg.norm(test1))
    if s.on_surface and cos_theta < 1/2:
        backTrack_length = math.hypot(x_next-sx, y_next-sy)
        ratio = abs(s.y_speed) / abs(s.x_speed)
        a = backTrack_length / math.sqrt(1 + ratio**2)
        b = a * ratio
        s.x += a * int(np.sign(s.x_speed))
        s.y += b * int(np.sign(s.y_speed))


def draw_spring(s, color, screen):
    if s.spring_unreleased:
        return
    a, b = get_tengential_component(s.x, s.y, s.x_spring, s.y_spring, s.size)
    a += s.x
    b += s.y
    py.draw.line(screen, color, (a, b), (s.x_spring, s.y_spring), 2)


def draw_all_obs(list_obs, color, screen):
    for o in list_obs:
        py.draw.rect(screen, color, o)

def draw_spider(s, color, screen):
    a = round(s.x)
    b = round(s.y)

    s.rect = py.draw.circle(screen, color, (a, b), s.size)

