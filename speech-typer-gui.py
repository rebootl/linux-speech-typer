#!/usr/bin/env python3
# NOTE: this example requires PyAudio because it uses the Microphone class

import argparse
import time
import speech_recognition as sr
import pyaudio

import PySimpleGUI as sg
from psgtray import SystemTray

from pynput.keyboard import Key, Controller

keyboard = Controller()

languages = [ 'en-US', 'de-DE' ]

keys = {
    'enter': Key.enter,
    'center': Key.enter,
    'hunter': Key.enter,
    'wetter': Key.enter,
    'space': Key.space,
    'keyspace': Key.space,
    'backspace': Key.backspace,
    'delete': Key.delete,
    'arrow left': Key.left,
    'arrow right': Key.right,
    'arrow write': Key.right,
    'arrow up': Key.up,
    'arrow down': Key.down,
    'tab': Key.tab,
    'tabulator': Key.tab,
    'page up': Key.page_up,
    'page down': Key.page_down,
}

replacements = {
    'equal': '=',
    'equals': '=',
    'equal spaced': ' = ',
    'dash': '-',
    'backtick': '`',
    'dollar sign': '$',
    'one': '1',
    'two': '2',
    'to': '2',
    'three': '3',
    'tree': '3',
    'free': '3',
    'for': '4',
    'four': '4',
    'five': '5',
    'six': '6',
    'seven': '7',
    'eight': '8',
    'nine': '9',
    'ten': '10',
    'eleven': '11',
    'twelve': '12',
    'thirteen': '13',
    'fourteen': '14',
    'fifteen': '15',
    'twenty': '20',
    'twentyfive': '25',
    'get pull': 'git pull',
    'get paul': 'git pull',
    'get push': 'git push',
    'get checkout': 'git checkout',
    'get branch': 'git branch',
    'get status': 'git status',
    'get log': 'git log',
}

def get_number(n):
    try:
        i = int(n)
        return i
    except ValueError:
        if (n in numbers):
            return numbers[n]
        return False

def press_key(k, n = 1):
    for c in range(n):
        keyboard.press(k)
        keyboard.release(k)

#def press_key_combo(ks):
#    with keyboard.pressed(ks[0]):
#        keyboard.press(ks[1])
#        keyboard.release(ks[1])

def get_words_without_number(words):
    n = get_number(words[-1:][0])
    if n:
        r = ' '.join(words[:-1])
    else:
        r = ' '.join(words)
    return r, n

def on_recognize(text):

    textlower = text.lower()

    if textlower in keys:
        press_key(keys[textlower])
    elif textlower in replacements:
        keyboard.type(replacements[textlower] + ' ')
    else:
        keyboard.type(textlower + ' ')

class SpeechTyper:

    def __init__(self, device):
        self.device = device
        self.language = languages[0]
        self.run_tray()

    # this is called from the background thread
    def callback(self, recognizer, audio):
        # received audio data, now we'll recognize it using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            print('~~~')
            self.tray.change_icon('icons/arrows.png')
            result = recognizer.recognize_google(audio, language = self.language)
            print('Result: ' + result)
            on_recognize(result)
            print('>>>')
            self.tray.change_icon('icons/active.png')
        except sr.UnknownValueError:
            print('...')
            self.tray.change_icon('icons/active.png')
        except sr.RequestError as e:
            print('Could not request results from Google Speech Recognition service; {0}'.format(e))
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

    def run_tray(self):
        menu = ['', [ 'Default language', languages, 'Pause/Resume listening', 'Exit']]
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

            elif event in languages:
                self.language = event
                if self.stop_listening:
                    self.stop_listening()
                    self.stop_listening = None
                    self.start_typer()

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
        #st.start_typer(ARGS.device)

if __name__ == '__main__':
    DEFAULT_SAMPLE_RATE = 16000

    parser = argparse.ArgumentParser(description="Stream from microphone to DeepSpeech using VAD")

    parser.add_argument('-l', '--list_devices', action='store_true',
                        help="List input device indexes.")
    parser.add_argument('-d', '--device', type=int, default=None,
                        help="Device input index (Int) as listed by -l.")

    ARGS = parser.parse_args()
    main(ARGS)
