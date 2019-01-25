'''
Rubics Cube
'''

import random, math, copy
import arcade

def intersect_lines(p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y):
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy-ay) * (bx-ax) > (by-ay) * (cx-ax)
    return ccw(p1x, p1y, p3x, p3y, p4x, p4y) != ccw(p2x, p2y, p3x, p3y, p4x, p4y) and ccw(p1x, p1y, p2x, p2y, p3x, p3y) != ccw(p1x, p1y, p2x, p2y, p4x, p4y)

BLUE = 0
ORANGE = 1
GREEN = 2
RED = 3
WHITE = 4
YELLOW = 5

sidename = ['BLUE', 'ORANGE', 'GREEN', 'RED', 'WHITE', 'YELLOW']
sideneighbors = [[4,3,5,1],
                 [4,0,5,2],
                 [4,1,5,3],
                 [4,2,5,0],
                 [3,0,1,2],
                 [1,0,3,2]]
sideconnections = [[0,5,0,3,1,7],
                   [3,0,5,0,3,3],
                   [0,3,0,5,7,1],
                   [5,0,3,0,5,5],
                   [7,7,7,7,0,0],
                   [1,1,1,1,0,0]]
connectedfaces = [[],[0,1,2],[],[6,3,0],[],[2,5,8],[],[8,7,6],[]]

cubeinit = ['000000000',
            '111111111',
            '222222222',
            '333333333',
            '444444444',
            '555555555']
            
sidecolors = [arcade.color.BLUE,
              arcade.color.ORANGE,
              arcade.color.GREEN,
              arcade.color.RED,
              arcade.color.WHITE,
              arcade.color.YELLOW]
              
subface = [[0,0,0,0,0,0,0,0,0],
           [1,1,1,1,1,1,1,1,1],
           [2,2,2,2,2,2,2,2,2],
           [3,3,3,3,3,3,3,3,3],
           [4,4,4,4,4,4,4,4,4],
           [5,5,5,5,5,5,5,5,5]]

perspective = 45

rotation_default_direction = [-1,-1,1,1,1,-1]
rotation_direction = 1
rotation_axis = [0,2,0,2,1,1]
rotation_angle = [0,0,0,0,0,0]
rotation_angle_step = 5
rotation_side = -1
animating = 0

def set_cube(configuration):
    if len(configuration)!=6:
        print('error in configuration:', configuration)
        return
    
    side = 0
    for c in configuration:
        if len(c)!=9:
            print('error in configuration:', configuration)
            return
        for i in range(9):
            subface[side][i] = int(c[i])
        
        side += 1

class Page:
    def __init__(self, width, height, overlay=True):
        self.buttons = []
        self.labels = []
        self.highlighted = None
        self.width = width
        self.height = height
        self.overlay = overlay        
        
    def add_button(self, x, y, w, h, image, func, tooltip=None):
        tex = arcade.load_texture(image)
        self.buttons.append([x, y, w, h, tex, func, tooltip])
        
    def add_label(self, text, x, y, color, size):
        self.labels.append([text, x, y, color, size])
        
    def draw(self):
        #draw UI
        for b in self.buttons:
            arcade.draw_texture_rectangle(b[0], b[1], b[2], b[3], b[4])
            if self.highlighted == b:
                arcade.draw_rectangle_outline(b[0], b[1], b[2], b[3], arcade.color.BLACK)
        for l in self.labels:
            arcade.draw_text(l[0], l[1], l[2], l[3], l[4], width=self.width, align="center", anchor_x="center", anchor_y="center")
            
    def mouse_over(self, x, y):
        self.highlighted = None
        for b in self.buttons:
            if x>=b[0]-b[2]/2 and x<=b[0]+b[2]/2 and y>=b[1]-b[3]/2 and y<=b[1]+b[3]/2:
                self.highlighted = b
                return b[6]
        return None
        
    def mouse_press(self, x, y):
        for b in self.buttons:
            if x>=b[0]-b[2]/2 and x<=b[0]+b[2]/2 and y>=b[1]-b[3]/2 and y<=b[1]+b[3]/2:
                b[5]()
                return True
                
        return False
        
class Game(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.status_default = 'Left click and drag to orbit. Right Click a face to rotate it clockwise (Hold ALT for counter-clockwise).'
        self.status = self.status_default
        
        self.pages = []
        
        # add UI page 0
        page = Page(width, height)
        self.pages.append(page)
        
        page.add_button(30, 570, 30, 30, '../images/action-undo-8x.png', self.undo_last_action, 'Undo')
        page.add_button(30, 530, 30, 30, '../images/action-redo-8x.png', self.redo_last_action, 'Redo')
        page.add_button(30, 470, 30, 30, '../images/box-8x.png', self.save_cube, 'Quick Save')
        page.add_button(30, 430, 30, 30, '../images/folder-8x.png', self.load_cube, 'Quick Load')
        page.add_button(30, 390, 30, 30, '../images/grid-three-up-8x.png', self.init_cube, 'Initialize Cube')
        page.add_button(30, 350, 30, 30, '../images/random-8x.png', self.jumble_cube, 'Randomize Cube')
        page.add_button(30, 90, 30, 30, '../images/question-mark-8x.png', self.show_help_page, 'Show help text')
        page.add_button(30, 50, 30, 30, '../images/account-logout-8x.png', arcade.close_window, 'Exit Program')
        
        self.current_page = 0
        
        # help page
        page = Page(width, height, False)
        self.pages.append(page)
        
        page.add_button(570, 570, 30, 30, '../images/circle-x-8x.png', self.show_ui_page, 'Return')
        
        page.add_label('Rubik\'s Cube', 300, 500, [0,0,0,200], 24)
        page.add_label('Click and Drag left mouse button to rotate the whole cube.', 300, 380, [0,0,0,150], 12)
        page.add_label('Click right mouse button on a side to rotate it clockwise (hold ALT to reverse).', 300, 360, [0,0,0,150], 12)
        page.add_label('Press Ctrl+Z or Ctrl+Shift+Z to undo ro redo. Ctrl+I to save current cube image.', 300, 340, [0,0,0,150], 12)
        page.add_label('Press Ctrl+S or Ctrl+O to save current or open last configuration.', 300, 320, [0,0,0,150], 12)
        page.add_label('Use Scroll wheel to zoom in and out.', 300, 300, [0,0,0,150], 12)
        page.add_label('Press R to randomize; I to initialize.', 300, 280, [0,0,0,150], 12)
        
        #
        arcade.set_background_color(arcade.color.WHITE)
        
        self.rotation_x = -20
        self.rotation_y = 210
        self.scale = 17
        self.translate_x = 300
        self.translate_y = 300
        
        self.left_mouse_down = False
        self.right_mouse_down = False
        
        self.action_history = []
        self.history_index = -1

        self.show_text = True
        
        self.polys_to_draw = []
        self.is_dirty = True
        
    def show_help_page(self):
        self.current_page = 1
        
    def show_ui_page(self):
        self.current_page = 0
        
    def init_cube(self):
        set_cube(cubeinit)
        
    def jumble_cube(self):
        self.action_history.clear()
        self.history_index = -1
        
        for i in range(100):
            side = random.choice(range(6))
            if random.choice((True,False)):
                self.rotate_side_ccw(side)
            else:
                self.rotate_side_cw(side)
            
    def save_cube(self):
        file = open('session.cube', 'w')
        for s in range(6):
            for f in range(9):
                file.write(str(subface[s][f]))
            file.write('\n')
        
        file.close()
        
    def load_cube(self):
        file = open('session.cube', 'r')
        config = file.read().splitlines()
        set_cube(config)
        file.close()
        
    def save_image(self):
        self.show_text = False
        self.on_draw()
        
        image = arcade.get_image()
        image.save('image.png', 'PNG')
        
        self.show_text = True
        
    def rotate(self, axis, cds, deg):
        if axis == 0:
            return self.rotatex(cds, deg)
        elif axis == 1:
            return self.rotatey(cds, deg)
        elif axis == 2:
            return self.rotatez(cds, deg)
            
    def rotatex(self, cds, deg):
        coords = copy.deepcopy(cds)
        rad = math.radians(deg)
        s = math.sin(rad)
        c = math.cos(rad)
        for i in range(9):
            for j in range(4):
                y = coords[i][j][1]
                z = coords[i][j][2]
                coords[i][j][1] = y * c - z * s #y cos θ − z sin θ
                coords[i][j][2] = y * s + z * c #y sin θ + z cos θ
        
        return coords
        
    def rotatey(self, cds, deg):
        coords = copy.deepcopy(cds)
        rad = math.radians(deg)
        s = math.sin(rad)
        c = math.cos(rad)
        for i in range(9):
            for j in range(4):
                x = coords[i][j][0]
                z = coords[i][j][2]
                coords[i][j][0] = x * c + z * s
                coords[i][j][2] = -x * s + z * c
        
        return coords
        
    def rotatez(self, cds, deg):
        coords = copy.deepcopy(cds)
        rad = math.radians(deg)
        s = math.sin(rad)
        c = math.cos(rad)
        for i in range(9):
            for j in range(4):
                x = coords[i][j][0]
                y = coords[i][j][1]
                coords[i][j][0] = x * c - y * s
                coords[i][j][1] = x * s + y * c
        
        return coords
        
    def rotatep(self, axis, p, s, c):
        if axis==0:
            return [p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c]
        if axis==1:
            return [p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c]
        if axis==2:
            return [p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2]]
            
    def setup(self):
        coords = []
        # left face
        size = 12
        size2 = size/2
        size3 = size/3
        x = -size2
        for y in range(3):
            for z in range(3):
                coords.append([[x, -size2 + y*size3, -size2 + z*size3],
                               [x, -size2 + y*size3, -size2 + z*size3 + size3],
                               [x, -size2 + y*size3 + size3, -size2 + z*size3 + size3],
                               [x, -size2 + y*size3 + size3, -size2 + z*size3]])
                
        self.face_coords = []
        self.face_coords.append(coords)
        
        self.face_coords.append(self.rotatey(coords, -90))
        self.face_coords.append(self.rotatey(coords, -180))
        self.face_coords.append(self.rotatey(coords, -270))
        self.face_coords.append(self.rotatez(coords, -90))
        self.face_coords.append(self.rotatez(coords, 90))
        
    def do_action(self, side, ccw = False):
        action = str(side)
        if ccw:
            self.rotate_side_ccw(side)
            action += 'cc'
        else:
            self.rotate_side_cw(side)
            action += 'cw'
            
        self.history_index += 1
        if len(self.action_history)>self.history_index:
            for i in range(len(self.action_history)-1, self.history_index-1, -1):
                del self.action_history[i]
                
        self.action_history.append(action)
        
    def redo_last_action(self):
        if self.history_index+1>=len(self.action_history):
            return
            
        self.history_index += 1
        action = self.action_history[self.history_index]
        side = int(action[0])
        if action[1:3]=='cc':
            self.rotate_side_ccw(side)
        else:
            self.rotate_side_cw(side)
            
    def undo_last_action(self):
        if self.history_index<0:
            return
            
        action = self.action_history[self.history_index]
        self.history_index -= 1
        
        side = int(action[0])
        if action[1:3]=='cc':
            self.rotate_side_cw(side)
        else:
            self.rotate_side_ccw(side)
            
    def right_mouse_pressed(self, x, y, alt_press=False):
        global rotation_direction, animating
        
        if animating>0:
            return
            
        ix = x + 1000
        
        found = False
        for si in range(6):
            # rotate the cube
            rc = self.rotatey(self.face_coords[si], self.rotation_y)
            rc = self.rotatex(rc, self.rotation_x)
            # which direction is the side facing
            # using the middle face of the side
            ax, ay, az = rc[4][0]
            bx, by, bz = rc[4][1]
            cx, cy, cz = rc[4][2]
            crz = (ax-bx)*(cy-by) - (ay-by)*(cx-bx)
            if crz>0: # only display facing sides
                faces = subface[si]
                for f in range(9):
                    coords = []
                    for i in range(4):
                        coords.append([rc[f][i][0]*self.scale+self.translate_x, rc[f][i][1]*self.scale+self.translate_y])
                        
                    icounts = 0
                    for p in range(4):
                        p1 = coords[p-1]
                        p2 = coords[p]
                        if intersect_lines(x, y, ix, y, coords[p-1][0], coords[p-1][1], coords[p][0], coords[p][1]):
                            icounts += 1
                    
                    if icounts==1:
                        found = True
                        break
            if found:
                break
                
        if found:
            self.selected_side = si
            self.selected_face = f
            #if f==4: # center face
            rotation_angle[si] = 90
            rotation_direction = rotation_default_direction[si]
            if alt_press:
                rotation_direction *= -1
            animating = 2
                
    def rotate_side_ccw(self, side):
        # rotate the side
        tmp = subface[side][0]
        subface[side][0] = subface[side][2]
        subface[side][2] = subface[side][8]
        subface[side][8] = subface[side][6]
        subface[side][6] = tmp
        tmp = subface[side][1]
        subface[side][1] = subface[side][5]
        subface[side][5] = subface[side][7]
        subface[side][7] = subface[side][3]
        subface[side][3] = tmp
        # rotate one for of each neighboring side
        lastside = sideneighbors[side][-1]
        sideconind = sideconnections[side][lastside] # which row to rotate / connected row
        tcf = connectedfaces[sideconind]
        tn6, tn7, tn8 = subface[lastside][tcf[0]],subface[lastside][tcf[1]],subface[lastside][tcf[2]]
        for n in sideneighbors[side]:
            sideconind = sideconnections[side][n] # which row to rotate / connected row
            tcf = connectedfaces[sideconind]
            subface[n][tcf[0]], tn6 = tn6, subface[n][tcf[0]]
            subface[n][tcf[1]], tn7 = tn7, subface[n][tcf[1]]
            subface[n][tcf[2]], tn8 = tn8, subface[n][tcf[2]]
        
    def rotate_side_cw(self, side):
        # rotate the side
        tmp = subface[side][6]
        subface[side][6] = subface[side][8]
        subface[side][8] = subface[side][2]
        subface[side][2] = subface[side][0]
        subface[side][0] = tmp
        tmp = subface[side][3]
        subface[side][3] = subface[side][7]
        subface[side][7] = subface[side][5]
        subface[side][5] = subface[side][1]
        subface[side][1] = tmp
        # rotate one for of each neighboring side
        lastside = sideneighbors[side][0]
        sideconind = sideconnections[side][lastside] # which row to rotate / connected row
        tcf = connectedfaces[sideconind]
        tn6, tn7, tn8 = subface[lastside][tcf[0]],subface[lastside][tcf[1]],subface[lastside][tcf[2]]
        for n in reversed(sideneighbors[side]):
            sideconind = sideconnections[side][n] # which row to rotate / connected row
            tcf = connectedfaces[sideconind]
            subface[n][tcf[0]], tn6 = tn6, subface[n][tcf[0]]
            subface[n][tcf[1]], tn7 = tn7, subface[n][tcf[1]]
            subface[n][tcf[2]], tn8 = tn8, subface[n][tcf[2]]
        
    class PolyToDraw:
        def __init__(self, z, coords, color):
            self.z = z
            self.coords = coords
            self.color = color
            
    def update(self, delta_time):
        global rotation_angle, animating, rotation_side
        
        if self.pages[self.current_page].overlay and self.is_dirty:
            
            self.is_dirty = animating>0
            
            #draw Cube
            self.polys_to_draw.clear()
            rotated = []
            
            # rotate for animation
            if animating == 1:
                self.do_action(rotation_side, rotation_direction != rotation_default_direction[rotation_side])
                animating = 0
            
            for side in range(6):
                if rotation_angle[side]==0:
                    rotated.append(copy.deepcopy(self.face_coords[side]))
                else:
                    rotated.append(self.rotate(rotation_axis[side], self.face_coords[side], (90-rotation_angle[side])*rotation_direction))
                
            for side in range(6):
                if rotation_angle[side]==0:
                    continue
                rad = math.radians((90-rotation_angle[side])*rotation_direction)
                sn = math.sin(rad)
                cs = math.cos(rad)
                for n in sideneighbors[side]:
                    sideconind = sideconnections[side][n]
                    cfs = connectedfaces[sideconind]
                    for cf in cfs:
                        for p in rotated[n][cf]:
                            p[0],p[1],p[2] = self.rotatep(rotation_axis[side], p, sn, cs)
                rotation_angle[side] -= rotation_angle_step
                if rotation_angle[side]==0:
                    animating = 1
                    rotation_side = side
                
            for si in range(6):
                # rotate the cube
                rc = self.rotatey(rotated[si], self.rotation_y)
                rc = self.rotatex(rc, self.rotation_x)
                faces = subface[si]
                for f in range(9):
                    # which direction is the side facing
                    # using the middle face of the side
                    ax, ay, az = rc[f][0]
                    bx, by, bz = rc[f][1]
                    cx, cy, cz = rc[f][2]
                    
                    az = (perspective-az)/perspective
                    bz = (perspective-bz)/perspective
                    cz = (perspective-cz)/perspective
                    crz = (ax*az-bx*bz)*(cy*cz-by*bz) - (ay*az-by*bz)*(cx*cz-bx*bz)
                    coords = []
                    avgz = 0
                    for i in range(4):
                        avgz += rc[f][i][2]
                        z = (perspective-rc[f][i][2])/perspective
                        coords.append([rc[f][i][0]*self.scale*z+self.translate_x, rc[f][i][1]*self.scale*z+self.translate_y])
                            
                    if crz>0:
                        self.polys_to_draw.append(Game.PolyToDraw(avgz/4, coords, sidecolors[faces[f]]))
                    else: # display backfaces as black
                        self.polys_to_draw.append(Game.PolyToDraw(avgz/4, coords, arcade.color.BLACK))
            
    def on_draw(self):
        arcade.start_render()
        
        self.pages[self.current_page].draw()
        
        if self.pages[self.current_page].overlay:
            
            # render polygons back to front (based on z depth)
            for p in sorted(self.polys_to_draw, key=lambda x: x.z, reverse=True):
                arcade.draw_polygon_filled(p.coords, p.color)
                arcade.draw_polygon_outline(p.coords, arcade.color.BLACK)
            
        # draw status bar
        status_text = self.status if self.status else self.status_default
        arcade.draw_text(status_text, 5, 5, [0,0,0,150], 10, width=600, align="left", anchor_x="left", anchor_y="bottom")
        
    def on_key_press(self, key, modifiers):
        if key == arcade.key.Z and modifiers & arcade.key.MOD_CTRL and modifiers & arcade.key.MOD_SHIFT:
            self.redo_last_action()
        elif key == arcade.key.Z and modifiers & arcade.key.MOD_CTRL:
            self.undo_last_action()
        elif key == arcade.key.R:
            self.jumble_cube()
        elif key == arcade.key.I and modifiers & arcade.key.MOD_CTRL:
            self.save_image()
        elif key == arcade.key.I:
            self.init_cube()
        elif key == arcade.key.S and modifiers & arcade.key.MOD_CTRL:
            self.save_cube()
        elif key == arcade.key.O and modifiers & arcade.key.MOD_CTRL:
            self.load_cube()
            
        self.is_dirty = True
        
    def on_mouse_motion(self, x, y, dx, dy):
        self.status = self.pages[self.current_page].mouse_over(x,y)
        if self.left_mouse_down:
            self.rotation_y -= dx
            self.rotation_x += dy
        
        self.is_dirty = True
        
    def on_mouse_press(self, x, y, button, modifiers):
        self.is_dirty = True
        
        if self.pages[self.current_page].mouse_press(x,y):
            return
            
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_down = True
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_pressed(x, y, modifiers & arcade.key.MOD_ALT)
            self.right_mouse_down = True
            
    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.left_mouse_down = False
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_mouse_down = False
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scale += scroll_y
        if self.scale<1: self.scale = 1
        if self.scale>35: self.scale = 35
        
        self.is_dirty = True
        
def main():
    game = Game(600, 600, 'Rubik\'s Cube')
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
    