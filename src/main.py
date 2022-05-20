'''
Rubics Cube
'''

import random
import math
import copy
import arcade


def intersect_lines(p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y):

    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

    return ccw(p1x, p1y, p3x, p3y, p4x, p4y) != ccw(
        p2x, p2y, p3x, p3y, p4x, p4y) and ccw(
            p1x, p1y, p2x, p2y, p3x, p3y) != ccw(p1x, p1y, p2x, p2y, p4x, p4y)


BLUE = 0
ORANGE = 1
GREEN = 2
RED = 3
WHITE = 4
YELLOW = 5

sidename = ['BLUE', 'ORANGE', 'GREEN', 'RED', 'WHITE', 'YELLOW']
sideneighbors = [[4, 3, 5, 1], [4, 0, 5, 2], [4, 1, 5, 3], [4, 2, 5, 0],
                 [3, 0, 1, 2], [1, 0, 3, 2]]
sideconnections = [[0, 5, 0, 3, 1, 7], [3, 0, 5, 0, 3, 3], [0, 3, 0, 5, 7, 1],
                   [5, 0, 3, 0, 5, 5], [7, 7, 7, 7, 0, 0], [1, 1, 1, 1, 0, 0]]
connectedfaces = [[], [0, 1, 2], [], [6, 3, 0], [], [2, 5, 8], [], [8, 7, 6],
                  []]

cubeinit = [
    '000000000', '111111111', '222222222', '333333333', '444444444',
    '555555555'
]

sidecolors = [
    arcade.color.BLUE, arcade.color.ORANGE, arcade.color.GREEN,
    arcade.color.RED, arcade.color.WHITE, arcade.color.YELLOW
]

perspective = 45

rotation_default_direction = [-1, -1, 1, 1, 1, -1]
rotation_direction = 1
rotation_axis = [0, 2, 0, 2, 1, 1]
rotation_angle = [0, 0, 0, 0, 0, 0]
rotation_angle_step = 5
rotation_side = -1
animating = 0

background_color = [210, 210, 220]


class Page:

    def __init__(self, width, height, overlay=True):
        self.buttons = []
        self.color_buttons = []
        self.labels = []
        self.steps = {}
        self.current_step = ''
        self.highlighted = None
        self.width = width
        self.height = height
        self.overlay = overlay

    def enable_default(self):
        return True

    def add_button(self,
                   x,
                   y,
                   w,
                   h,
                   image,
                   func,
                   tooltip=None,
                   enable_func=None):
        tex = arcade.load_texture(image)
        self.buttons.append([
            x, y, w, h, tex, func, tooltip,
            enable_func if enable_func else self.enable_default
        ])

    def add_color_button(self, x, y, w, h, color, func, tooltip=None):
        self.color_buttons.append(
            [x, y, w, h, color, func, tooltip, self.enable_default])

    def add_label(self, text, x, y, color, size):
        self.labels.append([text, x, y, color, size])

    def add_step(self, id, x, y, img, descrip):
        self.steps[id] = {'x': x, 'y': y,
                          'texture': arcade.load_texture(img),
                          'description': descrip}

    def draw(self):
        # draw UI
        for b in self.buttons:
            alpha = 255 if b[7]() else 180
            arcade.draw_texture_rectangle(b[0],
                                          b[1],
                                          b[2],
                                          b[3],
                                          b[4],
                                          alpha=alpha)
            if self.highlighted == b and b[7]():
                arcade.draw_rectangle_outline(b[0], b[1], b[2], b[3],
                                              arcade.color.BLACK)
        for b in self.color_buttons:
            arcade.draw_rectangle_filled(b[0], b[1], b[2], b[3], b[4])
            if self.highlighted == b:
                arcade.draw_rectangle_outline(b[0], b[1], b[2], b[3],
                                              arcade.color.BLACK)
        for l in self.labels:
            arcade.draw_text(l[0],
                             l[1],
                             l[2],
                             l[3],
                             l[4],
                             width=self.width,
                             align="center",
                             anchor_x="center",
                             anchor_y="center")

        if self.current_step != '':
            step = self.steps[self.current_step]
            arcade.draw_texture_rectangle(
                step['x'], step['y'], 50, 50, step['texture'])
            arcade.draw_text(step['description'], step['x'] +
                             40, step['y']+25, arcade.color.BLACK, anchor_y='top', multiline=True, width=400)

    def mouse_over(self, x, y):
        self.highlighted = None
        for b in self.buttons + self.color_buttons:
            if x >= b[0] - b[2] / 2 and x <= b[0] + b[2] / 2 and y >= b[
                    1] - b[3] / 2 and y <= b[1] + b[3] / 2:
                self.highlighted = b
                return b[6]
        return None

    def mouse_press(self, x, y):
        for b in self.buttons + self.color_buttons:
            if b[7] and x >= b[0] - b[2] / 2 and x <= b[0] + b[
                    2] / 2 and y >= b[1] - b[3] / 2 and y <= b[1] + b[3] / 2:
                b[5]()
                return True

        return False


class Game(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.cubepiece = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [1, 1, 1, 1, 1, 1, 1, 1, 1],
                          [2, 2, 2, 2, 2, 2, 2, 2, 2],
                          [3, 3, 3, 3, 3, 3, 3, 3, 3],
                          [4, 4, 4, 4, 4, 4, 4, 4, 4],
                          [5, 5, 5, 5, 5, 5, 5, 5, 5]]

        #
        arcade.set_background_color(background_color)

        # status bar
        self.status_default = 'Left click and drag to orbit. Right Click a face to rotate it clockwise (Hold ALT for counter-clockwise).'
        self.status = self.status_default

        self.pages = []

        # add UI page 0
        page = Page(width, height)
        self.pages.append(page)

        page.add_button(30, 570, 30, 30, 'images/action-undo-8x.png',
                        self.undo_last_action, 'Undo', self.enable_undo_button)
        page.add_button(30, 530, 30, 30, 'images/action-redo-8x.png',
                        self.redo_last_action, 'Redo', self.enable_redo_button)
        page.add_button(30, 470, 30, 30, 'images/box-8x.png', self.save_cube,
                        'Quick Save')
        page.add_button(30, 430, 30, 30, 'images/folder-8x.png',
                        self.load_cube, 'Quick Load')
        page.add_button(30, 390, 30, 30, 'images/grid-three-up-8x.png',
                        self.init_cube, 'Initialize Cube')
        page.add_button(30, 350, 30, 30, 'images/random-8x.png',
                        self.jumble_cube, 'Randomize Cube')
        page.add_button(30, 90, 30, 30, 'images/question-mark-8x.png',
                        self.show_help_page, 'Show help text')
        page.add_button(30, 50, 30, 30, 'images/account-logout-8x.png',
                        arcade.close_window, 'Exit Program')

        page.add_color_button(570, 570, 30, 30, arcade.color.BLUE,
                              self.show_blue, 'Orient to Blue face')
        page.add_color_button(570, 530, 30, 30, arcade.color.ORANGE,
                              self.show_orange, 'Orient to Orange face')
        page.add_color_button(570, 490, 30, 30, arcade.color.GREEN,
                              self.show_green, 'Orient to Green face')
        page.add_color_button(570, 450, 30, 30, arcade.color.RED,
                              self.show_red, 'Orient to Red face')
        page.add_color_button(570, 410, 30, 30, arcade.color.WHITE,
                              self.show_white, 'Orient to White face')
        page.add_color_button(570, 370, 30, 30, arcade.color.YELLOW,
                              self.show_yellow, 'Orient to Yellow face')

        page.add_step('daisy', 120, 570, 'images/daisy.jpeg',
                      'Make a daisy.\nYellow in the middle and white sides.')
        page.add_step('daisytocross', 120, 570, 'images/daisytocross.jpeg',
                      'Make white cross.\nRotate the upper layer (U) so the color matches up with front center layer.\nThen rotate the front layer (F) twice.')
        page.current_step = 'daisytocross'

        self.current_page = 0

        # help page
        page = Page(width, height, False)
        self.pages.append(page)

        page.add_button(570, 570, 20, 20, 'images/circle-x-8x.png',
                        self.show_ui_page, 'Return')

        page.add_label('Rubik\'s Cube', 300, 500, arcade.color.BLACK, 24)
        page.add_label(
            'Click and Drag left mouse button to rotate the whole cube.', 300,
            380, arcade.color.BLACK, 12)
        page.add_label(
            'Click right mouse button on a side to rotate it clockwise (hold ALT to reverse).',
            300, 360, arcade.color.BLACK, 12)
        page.add_label(
            'Press Ctrl+Z or Ctrl+Shift+Z to undo ro redo. Ctrl+I to save current cube image.',
            300, 340, arcade.color.BLACK, 12)
        page.add_label(
            'Press Ctrl+S or Ctrl+O to save current or open last configuration.',
            300, 320, arcade.color.BLACK, 12)
        page.add_label('Use Scroll wheel to zoom in and out.', 300, 300,
                       arcade.color.BLACK, 12)
        page.add_label('Press R to randomize; I to initialize.', 300, 280,
                       arcade.color.BLACK, 12)
        page.add_label('Author: Bhupendra Aole', 300, 100, arcade.color.BLACK,
                       15)
        page.add_label('Source: https://github.com/aole/Rubiks-Cube', 300, 75,
                       arcade.color.BLACK, 8)

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

    def enable_undo_button(self):
        return self.history_index >= 0

    def enable_redo_button(self):
        return self.history_index < len(self.action_history) - 1

    def show_blue(self):
        self.rotation_x = -20
        self.rotation_y = -110

    def show_orange(self):
        self.rotation_x = -20
        self.rotation_y = -20

    def show_green(self):
        self.rotation_x = -20
        self.rotation_y = 70

    def show_red(self):
        self.rotation_x = -20
        self.rotation_y = 160

    def show_white(self):
        self.rotation_x = -70
        self.rotation_y = 40

    def show_yellow(self):
        self.rotation_x = 70
        self.rotation_y = 40

    def show_help_page(self):
        self.current_page = 1

    def show_ui_page(self):
        self.current_page = 0

    def init_cube(self):
        self.set_cube(cubeinit)

    def set_cube(self, configuration):
        if len(configuration) != 6:
            print('error in configuration:', configuration)
            return

        side = 0
        for c in configuration:
            if len(c) != 9:
                print('error in configuration:', configuration)
                return
            for i in range(9):
                self.cubepiece[side][i] = int(c[i])

            side += 1

        self.derive_state()

    def jumble_cube(self):
        self.action_history.clear()
        self.history_index = -1
        self.state = 'Scambled'

        for i in range(100):
            side = random.choice(range(6))
            if random.choice((True, False)):
                self.rotate_side_ccw(side)
            else:
                self.rotate_side_cw(side)

    def save_cube(self):
        file = open('session.cube', 'w')
        for s in range(6):
            for f in range(9):
                file.write(str(self.cubepiece[s][f]))
            file.write('\n')

        file.close()

    def load_cube(self):
        file = open('session.cube', 'r')
        config = file.read().splitlines()
        self.set_cube(config)
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
                coords[i][j][1] = y * c - z * s  # y cos θ − z sin θ
                coords[i][j][2] = y * s + z * c  # y sin θ + z cos θ

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
        if axis == 0:
            return [p[0], p[1] * c - p[2] * s, p[1] * s + p[2] * c]
        if axis == 1:
            return [p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c]
        if axis == 2:
            return [p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2]]

    def setup(self):
        coords = []
        # left face
        size = 12
        size2 = size / 2
        size3 = size / 3
        x = -size2
        for y in range(3):
            for z in range(3):
                coords.append(
                    [[x, -size2 + y * size3, -size2 + z * size3],
                     [x, -size2 + y * size3, -size2 + z * size3 + size3],
                     [
                         x, -size2 + y * size3 + size3,
                         -size2 + z * size3 + size3
                    ], [x, -size2 + y * size3 + size3, -size2 + z * size3]])

        self.face_coords = []
        self.face_coords.append(coords)

        self.face_coords.append(self.rotatey(coords, -90))
        self.face_coords.append(self.rotatey(coords, -180))
        self.face_coords.append(self.rotatey(coords, -270))
        self.face_coords.append(self.rotatez(coords, -90))
        self.face_coords.append(self.rotatez(coords, 90))

    def derive_state(self):
        self.state = 'Scambled'
        solved = True

        # check white cross
        s = WHITE
        for i in range(1, 9, 2):
            if self.cubepiece[s][i] != int(cubeinit[s][i]):
                solved = False
                break
        if not solved:
            # check daisy
            s = YELLOW
            for i in range(1, 9, 2):
                if self.cubepiece[s][i] != int(cubeinit[WHITE][i]):
                    return
            self.state = 'Daisy'
            return
        self.state = 'White Cross'
        # check first layer
        s = WHITE
        for i in range(9):
            if self.cubepiece[s][i] != int(cubeinit[s][i]):
                return
        for s in range(6):
            if s in (WHITE, YELLOW):
                continue
            for i in range(3, 9, 3):
                if self.cubepiece[s][i-1] != int(cubeinit[s][i-1]):
                    return
        self.state = 'White Layer'
        # check middle layer
        self.state = 'Middle layer'
        # check yellow cross
        self.state = 'Yellow Cross'
        # check corners
        self.state = 'Solved'

    def do_action(self, side, ccw=False):
        action = str(side)
        if ccw:
            self.rotate_side_ccw(side)
            action += 'cc'
        else:
            self.rotate_side_cw(side)
            action += 'cw'

        self.history_index += 1
        if len(self.action_history) > self.history_index:
            for i in range(
                    len(self.action_history) - 1, self.history_index - 1, -1):
                del self.action_history[i]

        self.derive_state()
        print('State:', self.state)
        self.action_history.append(action)

    def redo_last_action(self):
        if self.history_index + 1 >= len(self.action_history):
            return

        self.history_index += 1
        action = self.action_history[self.history_index]
        side = int(action[0])
        if action[1:3] == 'cc':
            self.rotate_side_ccw(side)
        else:
            self.rotate_side_cw(side)

    def undo_last_action(self):
        if self.history_index < 0:
            return

        action = self.action_history[self.history_index]
        self.history_index -= 1

        side = int(action[0])
        if action[1:3] == 'cc':
            self.rotate_side_cw(side)
        else:
            self.rotate_side_ccw(side)

    def right_mouse_pressed(self, x, y, alt_press=False):
        global rotation_direction, animating

        if animating > 0:
            return

        found = False
        for si in range(6):
            # rotate the cube from initial orientation to display orientation
            rc = self.rotatey(self.face_coords[si], self.rotation_y)
            rc = self.rotatex(rc, self.rotation_x)
            # using the middle face of the side
            # use triangle orientation to find if the side is facing outwards
            ax, ay, az = rc[4][0]
            bx, by, bz = rc[4][1]
            cx, cy, cz = rc[4][2]
            crz = (ax - bx) * (cy - by) - (ay - by) * (cx - bx)
            if crz > 0:  # side is facing out
                # check each piece of the side of it intersects with mouse coords
                for f in range(9):
                    coords = []
                    for i in range(4):
                        coords.append([
                            rc[f][i][0] * self.scale + self.translate_x,
                            rc[f][i][1] * self.scale + self.translate_y
                        ])

                    # check if one of the sides intersections with a horizontal line on y
                    # only 1 should intersect to be in the polygon.
                    icounts = 0
                    for p in range(4):
                        p1 = coords[p - 1]
                        p2 = coords[p]
                        if intersect_lines(x, y, x+1000, y, coords[p-1][0],
                                           coords[p-1][1], coords[p][0],
                                           coords[p][1]):
                            icounts += 1

                    if icounts == 1:
                        found = True
                        break
            if found:
                break

        if found:
            self.selected_side = si
            self.selected_face = f
            # if f==4: # center face
            rotation_angle[si] = 90
            rotation_direction = rotation_default_direction[si]
            if alt_press:
                rotation_direction *= -1
            animating = 2

    def rotate_side_ccw(self, side):
        # rotate the side
        tmp = self.cubepiece[side][0]
        self.cubepiece[side][0] = self.cubepiece[side][2]
        self.cubepiece[side][2] = self.cubepiece[side][8]
        self.cubepiece[side][8] = self.cubepiece[side][6]
        self.cubepiece[side][6] = tmp
        tmp = self.cubepiece[side][1]
        self.cubepiece[side][1] = self.cubepiece[side][5]
        self.cubepiece[side][5] = self.cubepiece[side][7]
        self.cubepiece[side][7] = self.cubepiece[side][3]
        self.cubepiece[side][3] = tmp
        # rotate one for of each neighboring side
        lastside = sideneighbors[side][-1]
        sideconind = sideconnections[side][
            lastside]  # which row to rotate / connected row
        tcf = connectedfaces[sideconind]
        tn6, tn7, tn8 = self.cubepiece[lastside][tcf[0]], self.cubepiece[
            lastside][tcf[1]], self.cubepiece[lastside][tcf[2]]
        for n in sideneighbors[side]:
            sideconind = sideconnections[side][
                n]  # which row to rotate / connected row
            tcf = connectedfaces[sideconind]
            self.cubepiece[n][tcf[0]], tn6 = tn6, self.cubepiece[n][tcf[0]]
            self.cubepiece[n][tcf[1]], tn7 = tn7, self.cubepiece[n][tcf[1]]
            self.cubepiece[n][tcf[2]], tn8 = tn8, self.cubepiece[n][tcf[2]]

    def rotate_side_cw(self, side):
        # rotate the side
        tmp = self.cubepiece[side][6]
        self.cubepiece[side][6] = self.cubepiece[side][8]
        self.cubepiece[side][8] = self.cubepiece[side][2]
        self.cubepiece[side][2] = self.cubepiece[side][0]
        self.cubepiece[side][0] = tmp
        tmp = self.cubepiece[side][3]
        self.cubepiece[side][3] = self.cubepiece[side][7]
        self.cubepiece[side][7] = self.cubepiece[side][5]
        self.cubepiece[side][5] = self.cubepiece[side][1]
        self.cubepiece[side][1] = tmp
        # rotate one for of each neighboring side
        lastside = sideneighbors[side][0]
        sideconind = sideconnections[side][
            lastside]  # which row to rotate / connected row
        tcf = connectedfaces[sideconind]
        tn6, tn7, tn8 = self.cubepiece[lastside][tcf[0]], self.cubepiece[
            lastside][tcf[1]], self.cubepiece[lastside][tcf[2]]
        for n in reversed(sideneighbors[side]):
            sideconind = sideconnections[side][
                n]  # which row to rotate / connected row
            tcf = connectedfaces[sideconind]
            self.cubepiece[n][tcf[0]], tn6 = tn6, self.cubepiece[n][tcf[0]]
            self.cubepiece[n][tcf[1]], tn7 = tn7, self.cubepiece[n][tcf[1]]
            self.cubepiece[n][tcf[2]], tn8 = tn8, self.cubepiece[n][tcf[2]]

    class PolyToDraw:

        def __init__(self, z, coords, color):
            self.z = z
            self.coords = coords
            self.color = color

    def update(self, delta_time):
        global rotation_angle, animating, rotation_side

        if self.pages[self.current_page].overlay and self.is_dirty:

            self.is_dirty = animating > 0

            # draw Cube
            self.polys_to_draw.clear()
            rotated = []

            # rotate for animation
            if animating == 1:
                self.do_action(
                    rotation_side, rotation_direction !=
                    rotation_default_direction[rotation_side])
                animating = 0

            for side in range(6):
                if rotation_angle[side] == 0:
                    rotated.append(copy.deepcopy(self.face_coords[side]))
                else:
                    rotated.append(
                        self.rotate(
                            rotation_axis[side], self.face_coords[side],
                            (90 - rotation_angle[side]) * rotation_direction))

            for side in range(6):
                if rotation_angle[side] == 0:
                    continue
                rad = math.radians(
                    (90 - rotation_angle[side]) * rotation_direction)
                sn = math.sin(rad)
                cs = math.cos(rad)
                for n in sideneighbors[side]:
                    sideconind = sideconnections[side][n]
                    cfs = connectedfaces[sideconind]
                    for cf in cfs:
                        for p in rotated[n][cf]:
                            p[0], p[1], p[2] = self.rotatep(
                                rotation_axis[side], p, sn, cs)
                rotation_angle[side] -= rotation_angle_step
                if rotation_angle[side] == 0:
                    animating = 1
                    rotation_side = side

            for si in range(6):
                # rotate the cube
                rc = self.rotatey(rotated[si], self.rotation_y)
                rc = self.rotatex(rc, self.rotation_x)
                faces = self.cubepiece[si]
                for f in range(9):
                    # which direction is the side facing
                    # using the middle face of the side
                    ax, ay, az = rc[f][0]
                    bx, by, bz = rc[f][1]
                    cx, cy, cz = rc[f][2]

                    az = (perspective - az) / perspective
                    bz = (perspective - bz) / perspective
                    cz = (perspective - cz) / perspective
                    crz = (ax * az - bx * bz) * (cy * cz - by * bz) - (
                        ay * az - by * bz) * (cx * cz - bx * bz)
                    coords = []
                    avgz = 0
                    for i in range(4):
                        avgz += rc[f][i][2]
                        z = (perspective - rc[f][i][2]) / perspective
                        coords.append([
                            rc[f][i][0] * self.scale * z + self.translate_x,
                            rc[f][i][1] * self.scale * z + self.translate_y
                        ])

                    if crz > 0:
                        self.polys_to_draw.append(
                            Game.PolyToDraw(avgz / 4, coords,
                                            sidecolors[faces[f]]))
                    else:  # display backfaces as black
                        self.polys_to_draw.append(
                            Game.PolyToDraw(avgz / 4, coords,
                                            arcade.color.BLACK))

    def on_draw(self):
        arcade.start_render()

        self.pages[self.current_page].draw()

        if self.pages[self.current_page].overlay:

            # render polygons back to front (based on z depth)
            for p in sorted(self.polys_to_draw,
                            key=lambda x: x.z,
                            reverse=True):
                arcade.draw_polygon_filled(p.coords, p.color)
                arcade.draw_polygon_outline(p.coords, arcade.color.BLACK)

        # draw status bar
        status_text = self.status if self.status else self.status_default
        arcade.draw_text(status_text,
                         5,
                         5, [0, 0, 0, 150],
                         10,
                         width=600,
                         align="left",
                         anchor_x="left",
                         anchor_y="bottom")

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
        self.status = self.pages[self.current_page].mouse_over(x, y)
        if self.left_mouse_down:
            self.rotation_x += dy
            self.rotation_x %= 360
            if self.rotation_x > 120 and self.rotation_x < 300:
                self.rotation_y += dx
            else:
                self.rotation_y -= dx

        self.is_dirty = True

    def on_mouse_press(self, x, y, button, modifiers):
        self.is_dirty = True

        if self.pages[self.current_page].mouse_press(x, y):
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
        if self.scale < 1:
            self.scale = 1
        if self.scale > 35:
            self.scale = 35

        self.is_dirty = True


def main():
    game = Game(600, 600, 'Rubik\'s Cube')
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
