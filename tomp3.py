#!/usr/bin/python
import os, sys, subprocess, shlex, re, json, time
from subprocess import call

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

class MainScreen(Screen):
    pass

class WorkingScreen(Screen):
    pass

class RootScreen(ScreenManager):
    def showMainScreen():
        ScreenManager.current = 'mainscreen'

    def showWorkingScreen():
        ScreenManager.current = "workingscreen"


def convert(filename):
    # Get Bit Rate from source file
    #cmnd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=bit_rate,duration', '-of', 'json', filename]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    #print "==========output=========="
    #print out
    if err:
        print "========= error ========"
        print err
    else:
        parsed_json = json.loads(out)
        bit_rate = parsed_json['streams'][0]['bit_rate']
        print bit_rate + ":" + filename

        # Encode to MP3
        error = False
        filename_mp3 = os.path.splitext(filename)[0]+'.mp3'
        cmd = ['ffmpeg', '-y', '-i', filename, '-b:a', bit_rate, filename_mp3]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in p.stdout:
            if any(re.findall(r'error', line, re.IGNORECASE)):
                error = True
                print(line)

        if error:
            print "ERROR--->" + filename_mp3
            directory = os.path.dirname(filename) + '\\error\\'
            print directory
            if not os.path.exists(directory):
                os.makedirs(directory)

            print "MOVING-->" +  directory + os.path.basename(filename)
            os.rename(filename, directory + os.path.basename(filename))
            print "MOVING-->" +  directory + os.path.basename(filename_mp3)
            os.rename(filename_mp3, directory + os.path.basename(filename_mp3))

        else:
            print "-------->" + filename_mp3
            directory = os.path.dirname(filename) + '\\converted\\'
            print directory
            if not os.path.exists(directory):
                os.makedirs(directory)

            print "MOVING-->" +  directory + os.path.basename(filename)
            os.rename(filename, directory + os.path.basename(filename))


def on_mouse_move(x, y, modifiers):
    print x + ":" + y + "[" + modifiers +"]"
    return

def on_motion(self, etype, motionevent):
    # will receive all motion events.
    pass

class toMP3App(App):
    icon = "tomp3.png"
    title = "MP3 Convert!"

    def build(self):
        Window.size = (150, 150)
        Window.clearcolor = (1, 1, 1, 1)
        #Window.borderless = True

        Window.bind(on_dropfile=self._on_file_drop)
        Window.bind(on_mouse_move=on_mouse_move)
        Window.bind(on_motion=on_motion)
        return RootScreen()

    def _on_file_drop(self, window, file_path):
        #print(file_path)
        if any(re.findall(r'.wav|.m4a|.m4b|.wma', file_path, re.IGNORECASE)):
            convert(file_path)
        return

if __name__ == '__main__':
    toMP3 = toMP3App()
    toMP3.run()
