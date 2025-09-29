# Install dependencies
pkg update && pkg upgrade
pkg install python
pkg install chromium

pip install selenium

python bot.py
