'''
Rubics Cube
'''

import random, math, copy
import arcade

def intersect_lines(p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y):
    def ccw(ax, ay, bx, by, cx, cy):
        return (cy-ay) * (bx-ax) > (by-ay) * (cx-ax)
    return ccw(p1x, p1y, p3x, p3y, p4x, p4y) != ccw(p2x, p2y, p3x, p3y, p4x, p4y) and ccw(p1x, p1y, p2x, p2y, p3x, p3y) != ccw(p1x, p1y, p2x, p2y, p4x, p4y)

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

BLUE = 0
ORANGE = 1
GREEN = 2
RED = 3
WHITE = 4
YELLOW = 5

sidecolors = [arcade.color.BLUE,
              arcade.color.ORANGE,
              arcade.color.GREEN,
              arcade.color.RED,
              arcade.color.WHITE,
              arcade.color.YELLOW]
subface = [[],[],[],[],[],[]]

perspective = 45

def init_cude():
    color_remaining = [8,8,8,8,8,8]
    for i in range(6):
        for j in range(9):
            subface[i].append(i)

class Piece:
    def __init__(self, type, colors):
        self.type = type
        for t in range(type):
            self.colors[t] = colors[t]

class Cube:
    # 26 pieces
    # each piece has 1,2 or 3 colors
    # mid pieces have 1 color (which is the color of the side)
    # side pieces have 2 colors and cornor have 3
    def __init__(self):
        # define perfect/completed cube
        pass
        
class Game(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.WHITE)
        
        self.rotation_x = -30
        self.rotation_y = 40
        self.scale = 10
        self.translate_x = 300
        self.translate_y = 300
        
        self.left_mouse_down = False
        self.right_mouse_down = False
        
        self.action_history = []
        self.history_index = -1

    def jumble_cude(self):
        for i in range(100):
            side = random.choice(range(6))
            if random.choice((True,False)):
                self.rotate_side_ccw(side)
            else:
                self.rotate_side_cw(side)
            
    def rotatex(cds, deg):
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
        
    def rotatey(cds, deg):
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
        
    def rotatez(cds, deg):
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
        
    def setup(self):
        init_cude()
        self.jumble_cude()
        
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
        
        self.face_coords.append(Game.rotatey(coords, -90))
        self.face_coords.append(Game.rotatey(coords, -180))
        self.face_coords.append(Game.rotatey(coords, -270))
        self.face_coords.append(Game.rotatez(coords, -90))
        self.face_coords.append(Game.rotatez(coords, 90))
        
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
        ix = x + 1000
        
        found = False
        for si in range(6):
            # rotate the cube
            rc = Game.rotatey(self.face_coords[si], self.rotation_y)
            rc = Game.rotatex(rc, self.rotation_x)
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
            if f==4: # center face
                self.do_action(si, alt_press)
                
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
        
    def on_draw(self):
        arcade.start_render()
        
        for si in range(6):
            # rotate the cube
            rc = Game.rotatey(self.face_coords[si], self.rotation_y)
            rc = Game.rotatex(rc, self.rotation_x)
            # which direction is the side facing
            # using the middle face of the side
            ax, ay, az = rc[4][0]
            bx, by, bz = rc[4][1]
            cx, cy, cz = rc[4][2]
            az = (perspective-az)/perspective
            bz = (perspective-bz)/perspective
            cz = (perspective-cz)/perspective
            crz = (ax*az-bx*bz)*(cy*cz-by*bz) - (ay*az-by*bz)*(cx*cz-bx*bz)
            if crz>0: # only display facing sides
                faces = subface[si]
                for f in range(9):
                    coords = []
                    for i in range(4):
                        z = (perspective-rc[f][i][2])/perspective
                        #print(z)
                        coords.append([rc[f][i][0]*self.scale*z+self.translate_x, rc[f][i][1]*self.scale*z+self.translate_y])
                        
                    arcade.draw_polygon_filled(coords, sidecolors[faces[f]])
                    if self.right_mouse_down and self.selected_side==si and self.selected_face==f:
                        arcade.draw_polygon_outline(coords, arcade.color.BLACK, 3)
                    else:
                        arcade.draw_polygon_outline(coords, arcade.color.BLACK)
        
    def on_key_press(self, key, modifiers):
        if key == arcade.key.Z and modifiers & arcade.key.MOD_CTRL and modifiers & arcade.key.MOD_SHIFT:
            self.redo_last_action()
        elif key == arcade.key.Z and modifiers & arcade.key.MOD_CTRL:
            self.undo_last_action()
            
    def on_mouse_motion(self, x, y, dx, dy):
        if self.left_mouse_down:
            self.rotation_y -= dx
            self.rotation_x += dy
        
    def on_mouse_press(self, x, y, button, modifiers):
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
        
def main():
    game = Game(600, 600, 'Rubik\'s Cube')
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
    