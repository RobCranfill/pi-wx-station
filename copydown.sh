#!/bin/bash
# copy from Feathers to working dir
# assumes 'send' device is first CP drive
# TODO: could check for $CP/A.text to be sure

cp $CP/code.py ./code_send.py
cp $CP/send.py .
cp $CP/README.md .
cp $CP/settings.toml .

CP1=$CP'1'
cp $CP1/code.py ./code_rcv.py
cp $CP1/rcv.py .
cp $CP1/displayText.py .
cp $CP1/led8x8Font.py .
cp $CP1/LEDMatrix.py .

git status

