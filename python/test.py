import os, sys

text = "sda"
while True:
    print(text)
    os.execl(sys.executable, sys.executable, *sys.argv)
