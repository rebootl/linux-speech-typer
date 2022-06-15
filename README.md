# speech-typer-gui
Linux speech-to-text input w/ system tray

Once running spoken text will be typed at the current cursor location.

![screenshot](screenshot.png)

This is based on the python package [Uberi/speech_recognition](https://github.com/Uberi/speech_recognition) and uses the __Google Speech Recognition__ service. Different speech recognition backends are supported by [Uberi/speech_recognition](https://github.com/Uberi/speech_recognition) but currently not implemented here.

## Installation

I recommend using a virtual environment. However, for the system tray `tk` has to be installed system-wide:

    sudo apt-get install python3-tk

git clone the Repository or download the zip file and unzip it. And change into the directory.

    git clone https://github.com/rebootl/speech-typer-gui.git
    cd speech-typer-gui/

Setup and activate the virtual environment (optional):

    python3 -m venv env --system-site-packages
    . env/bin/activate

Install dependencies:

    pip3 install -r requirements.txt

Start:

    ./speech-typer-gui.py

The terminal should say `listening` and you should see the tray icon in the system tray.

To launch it in one step use: `/path-to-installation/env/bin/python /path-to-installation/speech-typer-gui.py`

## Configuration

Different language tags and replacements can be configured in `config.py`.

Find the relevant language codes here: https://cloud.google.com/speech-to-text/docs/languages
