#!/usr/bin/env python

import curses
import os


def debug(text):
    with open('/tmp/fileStuff.log', 'a') as f:
        f.write(str(text) + '\n')

class Colors(object):
    WHITE_ON_BLACK = 1
    WHITE_ON_BLUE = 2

class TextScreen(object):
    def __init__(self, screen):
        self.screen = screen
        self.screen.idlok(1)
        self.screen.scrollok(True)
        self.max_y, self.max_x = self.screen.getmaxyx()
        self.screen_buffer = []
        self.reset_screen()

    def add_line(self, text):
        self.draw_line(text)
        self.screen_buffer.append(text)

    def draw_line(self, text):
        self.cursor_y += 1
        self.text_height += 1
        self.screen.move(self.cursor_y, 0)
        self.screen.addstr(text)
        self.screen.move(self.cursor_y, 0)

    def replace_line_text(self, newText):
        selected_line = self.cursor_y
        self.screen_buffer[self.cursor_y] = newText
        self.draw_screen_from_buffer()
        self.move(selected_line)

    def get_line_text(self):
        text = self.screen.instr().strip()
        return text

    def draw_screen_from_buffer(self):
        self.reset_screen()
        for line in self.screen_buffer:
            self.draw_line(line)


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
        self.screen.attron(curses.color_pair(Colors.WHITE_ON_BLACK))
        self.screen.addstr(self.screen_buffer[from_y])

        # Set what our new line should be
        self.cursor_y = to_y

        # Now select current line
        self.screen.move(to_y, 0)
        self.screen.attron(curses.color_pair(Colors.WHITE_ON_BLUE))
        self.screen.addstr(self.screen_buffer[to_y])
        self.screen.move(to_y, 0)

        # Set the color back for the next time we draw
        self.screen.attron(curses.color_pair(Colors.WHITE_ON_BLACK))

        self.screen.refresh()

    def move_up(self):
        self.move(self.cursor_y - 1)

    def move_down(self):
        self.move(self.cursor_y + 1)

    def reset_screen(self):
        self.screen.erase()
        self.cursor_y = -1
        self.cursor_x = 0
        self.text_height = -1
        self.screen.move(0, 0)
        self.screen.refresh()


def paint_directory(screen, directory, show_dirs=True, show_hidden=False):
    screen.reset_screen()
    walker = os.walk(directory)
    current_dir, subdirs, files = walker.next()
    if show_dirs:
        if not directory == '/':
            screen.add_line('..')
        for dir in sorted(subdirs):
            # TODO: unnngh...window overflow...
            if screen.cursor_y+1 < screen.max_y:
                screen.add_line('/{}'.format(dir))
    for file_ in sorted(files):
        if not show_hidden and file_.startswith('.'):
            continue
        if screen.cursor_y+1 < screen.max_y:
            screen.add_line(file_)


def get_needed_digits(file_buffer):
    return len(str(len(file_buffer)))


def next_number_generator(file_buffer, total_digits=None):
    total_files = len(file_buffer)
    if not total_digits:
        total_digits = get_needed_digits(file_buffer)
    for number in range(1, total_files+1):
        # Probably a prettier way to do this...
        yield ('{:0' + str(total_digits) + '}').format(number)


def main(stdscr):
    screen = TextScreen(stdscr)

    # Setup color and cursor
    curses.start_color()
    curses.init_pair(Colors.WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(Colors.WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    screen.screen.attron(curses.color_pair(Colors.WHITE_ON_BLACK))
    curses.curs_set(0)

    # curses.newpad(lines, columns)  # TODO: figure this out!
    file_list = os.listdir(os.getcwd())
    paint_directory(screen, os.getcwd(), show_dirs=False, show_hidden=False)
    screen.move(0)
    # textbox = Textbox(screen.screen)

    needed_digits = get_needed_digits(screen.screen_buffer)
    next_number = next_number_generator(screen.screen_buffer, needed_digits)
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
            screen.replace_line_text('{}_{}'.format(next_number.next(), screen.get_line_text()))
        elif c == ord('s'):
            for new_name in screen.screen_buffer:
                original_name = new_name[needed_digits+1:]
                if original_name in file_list:
                    os.rename(original_name, new_name)
                else:
                    raise Exception("Didn't find original file for {}".format(new_name))
            break
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
