# Aufruf workshop_modul.py
import workshop_module

workshop_module.say_hello()
workshop_module.say_bye()

# Import Modul unter den Namen wm
import workshop_module as wm
wm.say_hello()
wm.say_bye()

# Import der Funktionen say_hello() aus Modul
from workshop_module import say_hello
say_hello()

# Import der Funktion say_bye als goodbye aus Modul
from workshop_module import say_bye as goodbye
goodbye()