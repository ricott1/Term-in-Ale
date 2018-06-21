
import pyxhook, time
from threading import Thread

#this function is called everytime a key is pressed.
def OnKeyPress(event):
    count += 1
    if event.Ascii==96: #96 is the ascii value of the grave key (`)
      new_hook.cancel()

def hook_thread():
    global count, new_hook
    #instantiate HookManager class
    new_hook=pyxhook.HookManager()
    #listen to all keystrokes
    new_hook.KeyDown=OnKeyPress
    #hook the keyboard
    new_hook.HookKeyboard()
    #start the session
    new_hook.start()

if __name__ == "__main__":
    thread = Thread(target = hook_thread)
    thread.start()
    #thread.join()
