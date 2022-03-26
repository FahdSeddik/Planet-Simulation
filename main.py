import pygame
import math
import random
pygame.init()


WIDTH,HEIGHT = 1600,900
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Planet Simulation")



#Colors to use later on
WHITE = (255,255,255)
CREAM = (247,226,226)
YELLOW = (255,255,0)
BLUE = (100,149,237)
RED = (188, 39, 50)
DARK_GREY = (80, 78 ,81)
ORANGE = (212,155,84)
PURPLE = (113,43,117)
#to initialize font
FONT = pygame.font.SysFont("comicsans", 16)

#button images
start_img = pygame.image.load('start_btn.png').convert_alpha()
exit_img = pygame.image.load('exit_btn.png').convert_alpha()
asteroid_img = pygame.image.load('asteroid.png').convert_alpha()

#button class
class Button():
    def __init__(self, x, y, image, s):
        w = image.get_width()
        h = image.get_height()
        self.image = image
        self.image = pygame.transform.scale(image, (int(w * s), int(h * s)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    
    def draw(self):
        action = False

        #we want to know where mouse is
        #get mouse position
        pos = pygame.mouse.get_pos()
        
        #check mouseover and clicked conditions
        #check collision with image rectangle
        if self.rect.collidepoint(pos):
            #if lmb clicked
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button on screen
        WIN.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Planet:
    #using astronomical units(AU) to simplify math
    #1 AU = 149.6e6 * 1000 m
    #dist from earth to sun = 1 AU
    AU = 149.6e6 * 1000
    #need gravitational constant
    G = 6.67428e-11
    #need scale to draw with
    # 1 AU is around 100 pixels
    SCALE = 160 / AU 
    #timestep represents how much time I want to simulate
    #how long before I take a step and simulate
    TIMESTEP = 3600*24  #1 day


    def __init__(self,x,y,radius,color,mass):
        # x,y in meters
        self.x=x 
        self.y=y
        self.radius=radius
        self.color=color
        self.mass=mass

        #to keep track of points moved to draw orbit
        self.orbit = []

        #to know if its sun to draw orbit or not
        self.sun = False

        self.distance_to_sun = 0
        self.x_vel = 0
        self.y_vel = 0

    #to draw takes window
    def draw(self,win):
        x = self.x * self.SCALE + WIDTH/2 # to shift 0,0 form top left
        y = self.y * self.SCALE + HEIGHT/2
        
        #need to draw its orbit
        #need to get x,y to scale
        
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                xo,yo = point
                xo = xo * self.SCALE + WIDTH/2
                yo = yo * self.SCALE + HEIGHT/2
                updated_points.append((xo,yo))
            #draw lines between points without enclosing them
            if not self.sun:
                pygame.draw.lines(win, self.color, False, updated_points)
        
        
        #draw circle
        pygame.draw.circle(win,self.color, (x,y), self.radius)

        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000)}km", 1, WHITE)
            win.blit(distance_text, (x-distance_text.get_width()/2,y-distance_text.get_height()/2))



    # we need to move planets around sun
    # we need to move planets in elliptical motion
    # thus we will move both x and y to simulate elliptical motion
    # We have to use Newton's law of universal gravitation
    # F = G(Mm/r^2)
    #
    #    /|planet
    # F / |
    #sun--|  Fy
    #   Fx
    def attraction(self,other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x **2 + distance_y **2)
        #calculated distance 
        #then put in distance to sun only if the passed other is
        #the sun
        if other.sun:
            self.distance_to_sun = distance

        #using Newton's law of universal gravitation
        force = self.G * self.mass * other.mass / distance**2
        #resolution of force components
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y
    

    
    def update_position(self,planets):
        total_fx = total_fy = 0
        #loop on planets and calculate velocity
        for planet in planets:
            if self == planet:
                continue
            fx,fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy
        
        #we need to calculate velocity
        #F = ma
        #v = Ft/m
        self.x_vel += total_fx/self.mass * self.TIMESTEP
        self.y_vel += total_fy/self.mass * self.TIMESTEP
        #to get position
        # dist = vt
        #total summation of all forces then we will get an elliptical orbit
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        
        self.orbit.append((self.x,self.y)) #put x,y in orbit array
        

asteroids = []

for i in range(0,100):
    r = random.randint(1,10)
    if r>5:
        nast = Planet(random.uniform(2,3)* Planet.AU,0,1,PURPLE,6 * 10**9)
        nast.y_vel=17.9 *1000
        nast.sun=True
    else:
        nast = Planet(-random.uniform(2,3)* Planet.AU,0,1,PURPLE,6 * 10**9)
        nast.y_vel=-17.9 *1000
        nast.sun=True
    asteroids.append(nast)

start_button = Button(0,0,start_img,0.2)
exit_button = Button(150,0,exit_img,0.2)
asteroid_button = Button(300,0,asteroid_img,0.2)

def main():
    run = True
    SIMULATE = False
    ASTEROIDS = False
    #to synchronize game with time not pc
    clock = pygame.time.Clock() 


    #using accurate masses in kg and initializing sun
    sun = Planet(0,0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True

    #planets
    mercury = Planet(0.4 * Planet.AU, 0, 8, DARK_GREY, 0.33 * 10**24)
    venus = Planet(0.723*Planet.AU, 0, 12, CREAM, 4.8685 * 10**24)
    earth = Planet(-1* Planet.AU, 0, 16, BLUE, 5.9742 * 10**24)
    mars = Planet(-1.524 * Planet.AU, 0, 14, RED, 6.39 * 10**23)
    jupiter = Planet(5.2 * Planet.AU, 0, 30, ORANGE, 1.899* 10**27)
    #need to give initial y velocity or else planets will get attracted to sun
    #and then no centripetal force
    #thus we add initial y vel
    # all in SI units (m/s)
    earth.y_vel = 29.783 * 1000
    mars.y_vel = 24.077 * 1000
    mercury.y_vel = 47.5 * 1000
    venus.y_vel = -35.02 * 1000
    jupiter.y_vel = 13.1 * 1000
    planets = [sun, earth, mars,mercury,venus,jupiter]
    start_button.draw()
    exit_button.draw()
    asteroid_button.draw()
    pygame.display.update()
    while run:
        clock.tick(60)
        WIN.fill((0,0,0))
        
        if start_button.draw():
            SIMULATE = True
        if exit_button.draw():
            SIMULATE = False
        if asteroid_button.draw():
            ASTEROIDS = not ASTEROIDS
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run= False
        
        if SIMULATE:
            for planet in planets:
                planet.update_position(planets)
                planet.draw(WIN)
            if ASTEROIDS:
                for asteroid in asteroids:
                    asteroid.update_position(planets)
                    asteroid.draw(WIN)
        
            pygame.display.update()

    pygame.quit()




main()