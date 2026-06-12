# Zahlen-Ratespiel
# 1. Rechner generiert eine Zahl zwischen 1 und 10#
# 2. Der Spieler gibt eine Zahl zwischen 1 und 10 ein#
# 3. Stimmt eingegebene mit generierter Zahl ueberein: gebe "Horaaaa! Deine Zahl {eingabe} ist richtig." aus#
# 4. Stimmt eingegebene mit generierter Zahl nicht überein: gebe "Oh je! Leider ist deine eingegebene Zahl {eingabe} nicht korrekt. Die richtige Zahl waere {generated} gewesen." aus


import random
print("Willkommen zum Zahlenraten-Spiel!")
print("Ich denke an eine Zahl zwischen 1 und 10.")

# Der Rechner generiert eine Zahl zwischen 1 und 10
randomzahl = random.randint(1, 10) 

# Der Spieler kann eine Zahl zwischen 1 und 10 eingeben!
userzahl = int(input("Gib mir eine Zahl zwischen 1 und 10: "))

# Sollte beide Zahlen gleich sein, dann kommt: "Horaaaa! Du hast die Zahl richtig erraten."
# Sonst:  "Oh nein, du hast leider eine falsche Zahl geraten, die richtige Zahl wäre {randomzahl}."
if randomzahl == userzahl:
    print("Huraaaa! Du hast die Zahl richtig erraten.")
else:
    print("Oh nein, du hast leider eine falsche Zahl geraten, die richtige Zahl wäre", randomzahl, "gewesen.")
#Spiel mit 3 Versuchen
import random

randomzahl = random.randint(1, 10) 
print("Willkommen zum Zahlenraten-Spiel!")
print("Ich denke an eine Zahl zwischen 1 und 10. Du hast 3 Versuche.")

for versuch in range(1, 4):
    userzahl = int(input("Gib eine Zahl zwischen 1 und 10 ein: "))

    if randomzahl == userzahl:
        print("Huraaaa! Du hast die Zahl richtig eingegeben!")
        break 
    else:
        # Dieser Block wird ausgeführt, wenn die Zahl falsch ist
        if versuch < 3:
            print("Leider falsch, probier es nochmal!")
        else:
            # Das passiert erst nach dem 3. Versuch
            print("Oh no, das war dein letzter Versuch. Die richtige Zahl wäre", randomzahl, "gewesen.")
    
#Spiel mit 3 Versuchen und Hinweis, ob die gesuchte Zahl größer oder kleiner ist
import random

randomzahl = random.randint(1, 10)
versuche_max = 3

print("Willkommen zum Zahlenraten-Spiel!")
print("Ich denke an eine Zahl zwischen 1 und 10. Du hast 3 Versuche.")

for versuch in range(1, versuche_max + 1):
    userzahl = int(input(f"\nVersuch {versuch}: Gib eine Zahl ein: "))

    if userzahl == randomzahl:
        print("Huraaaa! Du hast die Zahl richtig eingegeben!")
        break
    
    # Hier geben wir Tipps, solange man noch Versuche hat
    elif userzahl < randomzahl:
        print("Die gesuchte Zahl ist größer.")
    else:
        print("Die gesuchte Zahl ist kleiner.")

    # Ganz am Ende der Schleife auf letzten Versuch prüfen
    if versuch == versuche_max and userzahl != randomzahl:
        print("Oh no, das war dein letzter Versuch. Die richtige Zahl wäre", randomzahl, "gewesen.")