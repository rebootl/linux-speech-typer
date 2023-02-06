#!/usr/bin/env env/bin/python3
# NOTE: this example requires PyAudio because it uses the Microphone class

import argparse
import time
import speech_recognition as sr
import pyaudio
import json

import PySimpleGUI as sg
from psgtray import SystemTray

from pynput.keyboard import Controller

from config import *

keyboard = Controller()

def press_key(k, n = 1):
    for c in range(n):
        keyboard.press(k)
        keyboard.release(k)

#def press_key_combo(ks):
#    with keyboard.pressed(ks[0]):
#        keyboard.press(ks[1])
#        keyboard.release(ks[1])

class SpeechTyper:

    def __init__(self, device):
        self.device = device
        self.backend = 'vosk'
        self.model = 'model'
        self.language = languages[0]
        self.lowercase = True
        self.run_tray()

    def on_recognize(self, text):

        t = text.lower() if self.lowercase else text

        if t in keys:
            press_key(keys[t])
        elif t in replacements:
            keyboard.type(replacements[t] + ' ')
        else:
            keyboard.type(t + ' ')

    # this is called from the background thread
    def callback(self, recognizer, audio):
        print('~~~')
        self.tray.change_icon('icons/arrows.png')
        if self.backend == 'vosk':
            result = recognizer.recognize_vosk(audio, language = self.language)
            print(result)
            result = json.loads(result)['text']
        else:
            # received audio data, now we'll recognize it using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                result = recognizer.recognize_google(audio, language = self.language)
            except sr.UnknownValueError:
                print('...')
                self.tray.change_icon('icons/active.png')
            except sr.RequestError as e:
                print('Could not request results from Google Speech Recognition service; {0}'.format(e))
                self.tray.change_icon('icons/active.png')
        print('Result: ' + result)
        self.on_recognize(result)
        print('>>>')
        self.tray.change_icon('icons/active.png')
    def start_typer(self):
        r = sr.Recognizer()

        m = None
        if self.device:
            m = sr.Microphone()
        else:
            m = sr.Microphone(self.device)
        with m as source:
            #r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening
            r.energy_threshold = 300  # we only need to calibrate once, before we start listening
            r.dynamic_energy_threshold = False

        #from vosk import Model
        #r.vosk_model = Model(lang="en-us")

        # start listening in the background (note that we don't have to do this inside a `with` statement)
        self.stop_listening = r.listen_in_background(m, self.callback)
        print('listening')
        # `stop_listening` is now a function that, when called, stops background listening

        # do some unrelated computations for 5 seconds
        #for _ in range(50): time.sleep(1)  # we're still listening even though the main thread is doing other things

        # calling this function requests that the background listener stop listening
        #stop_listening(wait_for_stop=False)

        # do some more unrelated things
        #while True: time.sleep(0.1)  # we're not listening anymore, even though the background thread might still be running for a second or two while cleaning up and stopping

    def restart_listening(self):
        if self.stop_listening:
            self.stop_listening()
            self.stop_listening = None
            self.start_typer()

    def run_tray(self):
        backends = [ 'vosk', 'google' ]
        menu = ['', [ 'Backend', backends, 'Lowercase on/off', 'Default language',
                     languages, 'Pause/Resume listening', 'Exit']]
        tooltip = 'Tooltip'

        layout = [[sg.T('Empty Window', key='-T-')]]

        window = sg.Window('Window Title', layout, finalize=True, enable_close_attempted_event=True, alpha_channel=0)
        window.hide()

        tray = SystemTray(menu, single_click_events=False, window=window, tooltip=tooltip, icon='icons/active.png', key='-TRAY-')
        #tray.show_message('System Tray', 'System Tray Icon Started!')
        self.tray = tray
        print(sg.get_versions())

        self.start_typer()

        while True:
            event, values = window.read()
            # IMPORTANT step. It's not required, but convenient. Set event to value from tray
            # if it's a tray event, change the event variable to be whatever the tray sent
            if event == tray.key:
                event = values[event]  # use the System Tray's event as if was from the window

            if event in (sg.WIN_CLOSED, 'Exit'):
                break

            #tray.show_message(title=event, message=values)

            if event == 'Pause/Resume listening':
                if self.stop_listening:
                    self.stop_listening()
                    tray.change_icon('icons/inactive.png')
                    self.stop_listening = None
                else:
                    self.start_typer()
                    tray.change_icon('icons/active.png')

            elif event == 'Lowercase on/off':
                self.lowercase = not self.lowercase

            elif event in backends:
                self.backend = event
                self.restart_listening()

            elif event in languages:
                self.language = event
                self.restart_listening()

        tray.close()  # optional but without a close, the icon may "linger" until moused over
        window.close()


def list_devices():
    p = pyaudio.PyAudio()
    print('Devices:')
    for i in range(p.get_device_count()):
        d = p.get_device_info_by_index(i)
        print(f"{d['index']}: {d['name']}")

def main(ARGS):
    if ARGS.list_devices:
        list_devices()
    else:
        st = SpeechTyper(ARGS.device)

if __name__ == '__main__':
    DEFAULT_SAMPLE_RATE = 16000

    parser = argparse.ArgumentParser(description="Stream from microphone to DeepSpeech using VAD")

    parser.add_argument('-l', '--list_devices', action='store_true',
                        help="List input device indexes.")
    parser.add_argument('-d', '--device', type=int, default=None,
                        help="Device input index (Int) as listed by -l.")

    ARGS = parser.parse_args()
    main(ARGS)
