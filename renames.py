#!/usr/bin/env python

import curses
import os


def debug(text):
    with open('/tmp/fileStuff.log', 'a') as f:
        f.write(str(text) + '\n')


class TextScreen(object):
    def __init__(self, screen):
        self.screen = screen
        self.screen.idlok(1)
        self.screen.scrollok(True)
        self.max_y, self.max_x = self.screen.getmaxyx()
        self.reset()

    def add_line(self, text):
        self.cursor_y += 1
        self.text_height += 1
        self.screen.move(self.cursor_y, 0)
        self.screen.addstr(text)
        self.screen_buffer.append(text)
        self.screen.move(self.cursor_y, 0)

    # def move_left(self):
    #     self.cursor_x -= 1
    #     self.screen.move(self.cursor_y, self.cursor_x)
    #
    # def move_right(self):
    #     self.cursor_x += 1
    #     self.screen.move(self.cursor_y, self.cursor_x)

    def move(self, to_y):
        # First deselect the current text
        from_y, _ = self.screen.getyx()
        self.screen.move(from_y, 0)
        self.screen.clrtoeol()
        self.screen.attron(curses.color_pair(1))
        self.screen.addstr(self.screen_buffer[from_y])

        # Set what our new line should be
        self.cursor_y = to_y

        # Now select current line
        self.screen.move(to_y, 0)
        self.screen.attron(curses.color_pair(2))
        self.screen.addstr(self.screen_buffer[to_y])
        self.screen.move(to_y, 0)

        self.screen.refresh()

    def move_up(self):
        self.move(self.cursor_y - 1)

    def move_down(self):
        self.move(self.cursor_y + 1)

    def reset(self):
        self.screen.erase()
        self.screen_buffer = []
        self.cursor_y = -1
        self.cursor_x = 0
        self.text_height = -1
        self.screen.move(0, 0)
        self.screen.refresh()


def paint_directory(screen, directory, show_dirs=True, show_hidden=False):
    screen.reset()
    walker = os.walk(directory)
    current_dir, subdirs, files = walker.next()
    if show_dirs and not directory == '/':
        screen.add_line('..')
    for dir in sorted(subdirs):
        # TODO: unnngh...window overflow...
        if screen.cursor_y+1 < screen.max_y:
            screen.add_line('/{}'.format(dir))
    for file_ in sorted(files):
        if screen.cursor_y+1 < screen.max_y:
            screen.add_line(file_)


def main(stdscr):
    screen = TextScreen(stdscr)

    # Setup color and cursor
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
    screen.screen.attron(curses.color_pair(1))
    curses.curs_set(0)

    # curses.newpad(lines, columns)  # TODO: figure this out!
    paint_directory(screen, os.getcwd())
    screen.move(0)
    # textbox = Textbox(screen.screen)

            
    while True:
        c = stdscr.getch()
        if c == ord('q'):
            break
        elif c == curses.KEY_UP:
            if screen.cursor_y > 0:
                screen.move_up()
        elif c == curses.KEY_DOWN:
            if screen.cursor_y < screen.text_height:
                screen.move_down()
        elif c == ord(' '):
            text = screen.screen.instr().strip()
            debug(len(text))
        # elif c == curses.KEY_NPAGE:
        #     screen.screen.scroll(1)
        # elif c == curses.KEY_PPAGE:
        #     screen.screen.scroll(-1)
        # else:
        #     textbox.do_command(c)
        # if c == curses.KEY_UP:
        #     current_line -= 1
        #     screen.move(current_line, 0)
        # elif c == curses.KEY_DOWN:
        #     current_line += 1
        #     screen.move(current_line, 0)
    # text = textbox.gather()
    # print(text)

debug('new instance')
curses.wrapper(main)
