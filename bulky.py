#!/usr/bin/env python

import curses
import os

MAX_FILENAME_LENGTH = os.pathconf('.', 'PC_NAME_MAX')


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
        self.reset_screen()

    def add_line(self, text):
        if self.cursor_y+1 < self.max_y:
            self.cursor_y += 1
            self.text_height += 1
            self.screen.move(self.cursor_y, 0)
            self.screen.addstr(text)
            self.screen.move(self.cursor_y, 0)
        else:
            raise Exception("No more lines left!")

    def replace_line_text(self, newText):
        self.screen.move(self.cursor_y, 0)
        self.screen.clrtoeol()
        self.current_buffer[self.cursor_y] = newText
        self.screen.attron(curses.color_pair(Colors.WHITE_ON_BLUE))  # Current line was already selected
        self.screen.addstr(newText)
        self.screen.attron(curses.color_pair(Colors.WHITE_ON_BLACK))

    def get_line_text(self):
        text = self.screen.instr().strip()
        return text

    def draw_screen(self, buffer):
        self.reset_screen()
        self.current_buffer = buffer
        for line in buffer:
            if not self.cursor_y == self.max_y:
                self.add_line(line)

    def select_line(self, to_y):
        # First deselect the current text
        from_y, _ = self.screen.getyx()
        self.screen.move(from_y, 0)
        self.screen.clrtoeol()
        self.screen.attron(curses.color_pair(Colors.WHITE_ON_BLACK))
        self.screen.addstr(self.current_buffer[from_y])

        # Set what our new line should be
        self.cursor_y = to_y

        # Now select current line
        self.screen.move(to_y, 0)
        self.screen.attron(curses.color_pair(Colors.WHITE_ON_BLUE))
        self.screen.addstr(self.current_buffer[to_y])
        self.screen.move(to_y, 0)

        # Set the color back for the next time we draw
        self.screen.attron(curses.color_pair(Colors.WHITE_ON_BLACK))

        self.screen.refresh()

    def move_up(self):
        self.select_line(self.cursor_y - 1)

    def move_down(self):
        self.select_line(self.cursor_y + 1)

    def reset_screen(self):
        self.current_buffer = []
        self.screen.erase()
        self.cursor_y = -1
        self.cursor_x = 0
        self.text_height = -1
        self.screen.move(0, 0)
        self.screen.refresh()


class FileManager(object):
    def __init__(self, directory=os.curdir, show_dirs=True, show_hidden=False):
        self.files = self.generate_file_list(directory, show_dirs, show_hidden)
        self.changes = {}
        for entry in self.files:
            self.changes[entry] = None

    def generate_file_list(self, directory, show_dirs, show_hidden):
        walker = os.walk(directory)
        current_dir, subdirs, files = walker.next()
        file_list = []
        # This is slightly awkward because we want dirs first in the list
        if show_dirs:
            if not directory == '/':
                file_list.append('..')
            for dir in sorted(subdirs):
                if show_hidden or not dir.startswith('.'):
                    file_list.append('/{}'.format(dir))
        for file_ in sorted(files):
            if show_hidden or not file_.startswith('.'):
                file_list.append(file_)
        return file_list


def get_needed_digits(file_buffer):
    return len(str(len(file_buffer)))


def next_number_generator(file_buffer, total_digits=None):
    total_files = len(file_buffer)
    if not total_digits:
        total_digits = get_needed_digits(file_buffer)
    for number in range(1, total_files+1):
        # Probably a prettier way to do this...
        yield ('{:0' + str(total_digits) + '}').format(number)


def create_command_bar(screen):
    new_screen = curses.newwin(1, screen.max_x, screen.max_y-2, 0)
    new_screen.addstr("hi")
    new_screen.refresh()

def main(stdscr):
    screen = TextScreen(stdscr)

    # # Setup color and cursor
    curses.start_color()
    curses.init_pair(Colors.WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(Colors.WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    screen.screen.attron(curses.color_pair(Colors.WHITE_ON_BLACK))
    curses.curs_set(0)

    dir = FileManager(os.getcwd(), show_dirs=False, show_hidden=False)
    screen.draw_screen(dir.files)
    screen.select_line(0)


    # Textbox?
    # textbox = Textbox(screen.screen)

    needed_digits = get_needed_digits(dir.files)
    next_number = next_number_generator(dir.files, needed_digits)
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
            old_text = screen.get_line_text()
            new_text = '{}_{}'.format(next_number.next(), old_text)
            dir.changes[old_text] = new_text
            screen.replace_line_text(new_text)
        elif c == ord('s'):
            for old_name, new_name in dir.changes.items():
                if new_name:
                    # Just letting exceptions bubble up for now...
                    os.rename(old_name, new_name)
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
