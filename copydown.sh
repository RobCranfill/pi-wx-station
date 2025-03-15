#!/bin/bash
# copy from Feathers to working dir
# assumes 'send' device is first CP drive

cp $CP/send.py .
cp $CP/README.md .
cp $CP/settings.toml .

CP1=$CP'1'
cp $CP1/rcv.py .
cp $CP1/displayText.py .
cp $CP1/led8x8Font.py .
cp $CP1/LEDMatrix.py .

git status

