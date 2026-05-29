# Definiere Klasse KFZ mit Attributen hersteller und kennzeichen.
# Erzeuge zwei Fahrzeuge: 
#     Variable bmw mit BMW mit Kennzeichen M-BW 123
#     Variable vw mit VW mit Kennzeichen WOB-VW 246
# Erzeuge neue Instanz von KFZ mit gleichen Attributen wie bmw:
#     Variable bmw2 mit BMW mit Kennzeichen M-BW 123
# Vergleiche alls KFZ, ob diese gleich sind bmw, bmw2, vw.
# Methode melde_um, welche Kennzeichen auf Argument neues_kennzeichen veraendert.
# Melde VW auf neues Kennzeichen BGL-A 9 um und pruefe Erfolg
# Melde bmw auf F-B21 um und pruefe ob bmw2 sich aendert 

class KFZ:
    def __init__(self, hersteller, kennzeichen):
        self.hersteller = hersteller
        self.kennzeichen = kennzeichen
    
    def __str__(self):
        return f"{self.hersteller} mit Kennzeichen {self.kennzeichen}"
    
    def __eq__(self, other):
        if not isinstance(other, KFZ):
            return False
        return self.hersteller == other.hersteller and self.kennzeichen == other.kennzeichen
        
    def melde_um(self, neues_kennzeichen):
        self.kennzeichen = neues_kennzeichen

# --- KFZ-Instanzen erstellen ---

bmw = KFZ('BMW', 'M-BW 123')
vw = KFZ('VW', 'WOB-VW 246')
bmw2 = KFZ('BMW', 'M-BW 123')

# Inhaltsvergleich der KFZ-Objekte
# 1. Vergleich 1: vw mit bmw
if vw.hersteller == bmw.hersteller and vw.kennzeichen == bmw.kennzeichen:
    print("vw und bmw sind gleich.")
else:
    print("vw und bmw sind unterschiedlich.")

# 2. Vergleich: vw mit bmw2
if vw.hersteller == bmw2.hersteller and vw.kennzeichen == bmw2.kennzeichen:
    print("vw und bmw2 sind gleich.")
else:
   print("vw und bmw2 sind unterschiedlich.")

# 3. Vergleich: bmw mit bmw2
if bmw.hersteller == bmw2.hersteller and bmw.kennzeichen == bmw2.kennzeichen:
    print("bmw und bmw2 sind gleich.")
else:
    print("bmw und bmw2 sind unterschiedlich.")

# Identitätsvergleich der KFZ-Objekte
if vw is bmw:
    print("vw und bmw sind identisch.")
else:
    print("vw und bmw sind nicht identisch.")
if vw is bmw2:
    print("vw und bmw2 sind identisch.")   
else:
    print("vw und bmw2 sind nicht identisch.")
if bmw is bmw2:
    print("bmw und bmw2 sind identisch.")
else:
    print("bmw und bmw2 sind nicht identisch.")

# Vergleich alternativ mit __eq__ Methode, diese wird mit == Operator aufgerufen
print(f"bmw2 == bmw: {bmw2 == bmw}")
print(f"vw == bmw: {vw == bmw}")
print(f"vw == bmw2: {vw == bmw2}")

# VW ummelden
vw.melde_um('BGL-A 9')
if vw.kennzeichen == 'BGL-A 9': # prüfe auf Erfolg
    print('VW umgemeldet.')

# BMW ummelden und bmw2 prüfen
bmw.melde_um('F-B21')

if str(bmw2) != str(bmw):
    print('bmw wurde geändert, bmw2 ist unverändert geblieben.')

print(f"bmw:  {bmw}")
print(f"bmw2: {bmw2}")