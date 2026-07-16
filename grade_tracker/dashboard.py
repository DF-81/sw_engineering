import gradio as gr
from pathlib import Path
from notenverwaltung.models.student import Student
from notenverwaltung.models.course import Course
from notenverwaltung.models.grade import Grade
from notenverwaltung.storage.sqlite_store import SqliteGradeStore
from notenverwaltung.gradebook import GradeBook
from notenverwaltung.reports.base import TextReportGenerator, CsvReportGenerator

DB_PATH = "noten.db"
# 1. We create the relational SQLite-Store
store = SqliteGradeStore(DB_PATH)
# 2. We inject the store into the GradeBook (exactly as required in the UML diagram)
gb = GradeBook(store=store)

# --- LOGIN-VERIFICATION for the employees ---
def mitarbeiter_einloggen(benutzername, passwort):
    if benutzername == "admin" and passwort == "geheim123":
        return (
            "🔓 Login erfolgreich! Die Mitarbeiter-Bereiche wurden freigeschaltet.", 
            gr.update(visible=True), 
            gr.update(visible=True),
            gr.update(visible=True)
        )
    else:
        return "❌ Fehler: Ungültige Zugangsdaten. Zugriff verweigert.", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

def mitarbeiter_ausloggen():
    return (
        "🔒 Erfolgreich abgemeldet. Die Bereiche wurden wieder gesperrt.", 
        gr.update(visible=False), 
        gr.update(visible=False),
        gr.update(visible=False)
    )

# --- BACKEND LOGIC (with refactoring it has delegate to the Gradebook) ---
def note_loeschen(note_id):
    if not note_id:
        return "❌ Fehler: Bitte eine Noten-ID eingeben!"
    try:
        # Direct connection to the store to delete an grade ID
        with gb.store._conn:
            cursor = gb.store._conn.cursor()
            cursor.execute("SELECT * FROM grades WHERE id = ?;", (int(note_id),))
            if not cursor.fetchone():
                return f"❌ Fehler: Keine Note mit der ID '{note_id}' gefunden."
            
            cursor.execute("DELETE FROM grades WHERE id = ?;", (int(note_id),))
            gb.store._conn.commit()
        return f"🗑️ Erfolg: Kurs-Note mit ID {note_id} wurde entfernt!"
    except ValueError:
        return "❌ Fehler: Die Noten-ID muss eine Zahl sein!"
    except Exception as e:
        return f"❌ Fehler beim Löschen: {str(e)}"

def frontend_report_erstellen(student_id, datei_format):
    if not student_id:
        return "❌ Fehler: Bitte geben Sie eine Studenten-ID ein!"
        
    s_id_clean = student_id.strip().upper()
    
    if "Text" in datei_format:
        generator = TextReportGenerator()
    else:
        generator = CsvReportGenerator()
        
    return generator.generate_student_report(s_id_clean, gb)

def noten_liste_aktualisieren(s_id):
    if not s_id:
        return "Bitte geben Sie links eine Studenten-ID ein, um dessen Noten zu laden."
    
    s_id_clean = s_id.strip().upper()
    all_grades = gb.get_student_grades(s_id_clean)
    
    if not all_grades:
        return f"Keine Noten für Student ID '{s_id_clean}' in der Datenbank gefunden."
    
    text = f"📋 Notenblatt für Student-ID: {s_id_clean}\n"
    text += "="*50 + "\n"
    
    # By getting real Grade-Objects from the GradeBook, we can organize the logc via Python-Properties
    with gb.store._conn:
        cursor = gb.store._conn.cursor()
        for g in all_grades:
            # here we fetch the real generated SQLite ID for display
            cursor.execute("SELECT id FROM grades WHERE student_id=? AND course_id=? AND score=? AND date=?;",
                           (g.student.student_id, g.course.course_id, g.score, g.date))
            row = cursor.fetchone()
            g_id = row["id"] if row else "?"
            
            status = "PASSED" if g.is_passing else "FAILED"
            text += f"🆔 GRADE-ID: {g_id}\n"
            text += f"📘 Kurs: {g.course.name} ({g.course.course_id})\n"
            text += f"   Punkte: {g.score}/{g.course.max_grade} ({g.letter_grade}) -> [{status}]\n"
            if g.notes:
                text += f"   Notiz: {g.notes}\n"
            text += f"   Datum: {g.date}\n"
            text += "-"*50 + "\n"
            
    return text

def student_hinzufuegen(s_id, vorname, nachname, email):
    try:
        if not s_id or not vorname or not nachname or not email:
            return "❌ Fehler: Alle Felder müssen ausgefüllt sein!"
        
        s_id_clean = s_id.strip().upper()
        neuer_student = Student(s_id_clean, vorname.strip(), nachname.strip(), email.strip())
        gb.add_student(neuer_student)
        return f"✅ Erfolg: Student {vorname} {nachname} ({s_id_clean}) über GradeBook in DB gespeichert!"
    except ValueError as e: return f"❌ Fehler: {str(e)}"

def student_loeschen(s_id):
    if not s_id: return "❌ Fehler: Bitte eine Studenten-ID eingeben!"
    s_id_clean = s_id.strip().upper()
    try:
        with gb.store._conn:
            cursor = gb.store._conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?;", (s_id_clean,))
            if not cursor.fetchone():
                return f"❌ Fehler: Student '{s_id_clean}' existiert nicht."
            cursor.execute("DELETE FROM students WHERE student_id = ?;", (s_id_clean,))
            gb.store._conn.commit()
        return f"🗑️ Erfolg: Student '{s_id_clean}' komplett gelöscht!"
    except Exception as e: return f"❌ Fehler: {str(e)}"

def kurs_hinzufuegen(c_id, name, max_g, pass_g):
    try:
        if not c_id or not name:
            return "❌ Fehler: ID und Name müssen ausgefüllt sein!"
        
        c_id_clean = c_id.strip().upper()
        neuer_kurs = Course(c_id_clean, name.strip(), float(max_g), float(pass_g)) 
        gb.add_course(neuer_kurs)
        return f"✅ Erfolg: Kurs '{name}' ({c_id_clean}) über GradeBook in DB gespeichert!"
    except ValueError as e: return f"❌ Fehler: {str(e)}"

def note_eintragen(s_id, c_id, score, datum, notiz):
    try:
        s_id_clean = s_id.strip().upper()
        c_id_clean = c_id.strip().upper()
        
        # The GradeBook is taking over the wohle creation and saving process!
        gb.record_grade(s_id_clean, c_id_clean, float(score), datum.strip(), notiz.strip())
        return f"✅ Erfolg: Note über GradeBook sicher in DB verbucht!"
    except ValueError as e:
        return f"❌ Fehler: {str(e)}"

# --- GRAPHICAL INTERFACE DESIGN ---
with gr.Blocks(title="Persistent Grade Tracker") as demo:
    gr.Markdown("# 🗄️ Relationaler Student Grade Tracker (UML-Architektur)")
    gr.Markdown("Dieses Dashboard nutzt die geforderte Store-Abstraktion via Dependency Injection.")

    # REITER 1: Public area
    with gr.Tab("🔍 Mein Notenblatt (Öffentlich)"):
        gr.Markdown("### Schau dir deine Noten an")
        search_sid = gr.Textbox(label="Gib deine Studenten-ID ein (z.B. S123)")
        btn_refresh = gr.Button("🔄 Noten abrufen", variant="primary")
        noten_anzeige = gr.TextArea(label="Deine Noten", lines=15)
        
        btn_refresh.click(noten_liste_aktualisieren, inputs=[search_sid], outputs=noten_anzeige)

    # REITER 2: LOGIN & LOGOUT
    with gr.Tab("🔐 Mitarbeiter-Login"):
        gr.Markdown("### Interner Bereich für Lehrkräfte und Verwaltung")
        with gr.Row():
            user_input = gr.Textbox(label="Benutzername")
            pass_input = gr.Textbox(label="Passwort", type="password")
        with gr.Row():
            btn_login = gr.Button("Anmelden", variant="secondary")
            btn_logout = gr.Button("Abmelden", variant="stop")
        login_status = gr.Textbox(label="Status")

    # REITER 3: Student organization
    with gr.Tab("👤 Stammdaten verwalten", visible=False) as tab_verwaltung:
        gr.Markdown("### 🟢 Neuen Studenten registrieren")
        with gr.Row():
            s_id = gr.Textbox(label="Studenten-ID (z.B. S123)")
            vorname = gr.Textbox(label="Vorname")
            nachname = gr.Textbox(label="Nachname")
            email = gr.Textbox(label="E-Mail-Adresse")
        btn_student = gr.Button("Student permanent speichern", variant="primary")
        output_student = gr.Textbox(label="Status Speicherung")
        
        gr.Markdown("---")
        gr.Markdown("### 📘 Neuen Kurs anlegen")
        with gr.Row():
            c_id = gr.Textbox(label="Kurs-ID (z.B. CS101)")
            c_name = gr.Textbox(label="Kursname")
            max_grade = gr.Number(label="Maximalpunkte", value=100.0)
            pass_grade = gr.Number(label="Bestehensgrenze", value=50.0)
        btn_kurs = gr.Button("Kurs permanent speichern", variant="primary")
        output_kurs = gr.Textbox(label="Status Kurs")
        
        gr.Markdown("---")
        gr.Markdown("### 🔴 Kompletten Studenten entfernen")
        delete_id = gr.Textbox(label="Studenten-ID zum Löschen")
        btn_delete = gr.Button("Student samt aller Noten unwiderruflich löschen", variant="stop")
        output_delete = gr.Textbox(label="Status Löschung")

        btn_student.click(student_hinzufuegen, inputs=[s_id, vorname, nachname, email], outputs=output_student)
        btn_kurs.click(kurs_hinzufuegen, inputs=[c_id, c_name, max_grade, pass_grade], outputs=output_kurs)
        btn_delete.click(student_loeschen, inputs=[delete_id], outputs=output_delete)

    # REITER 4: Grade organization
    with gr.Tab("📝 Noten verbuchen & entfernen", visible=False) as tab_noten:
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🖊️ Neue Note eintragen")
                g_sid = gr.Textbox(label="Studenten-ID")
                g_cid = gr.Textbox(label="Kurs-ID")
                g_score = gr.Number(label="Erreichte Punkte")
                g_date = gr.Textbox(label="Datum (YYYY-MM-DD)", value="2026-07-12")
                g_notes = gr.Textbox(label="Anmerkung")
                btn_note = gr.Button("Note buchen", variant="primary")
                output_note = gr.Textbox(label="Status Buchung")
                gr.Markdown("---")
                gr.Markdown("### 🗑️ Einzelnen Kurs/Note bei Student entfernen")
                delete_gid = gr.Textbox(label="GRADE-ID eingeben (aus der rechten Abfrage ablesen)")
                btn_del_grade = gr.Button("Diese einzelne Note löschen", variant="stop")
                output_del_grade = gr.Textbox(label="Status Noten-Löschung")
            with gr.Column():
                gr.Markdown("### 🔍 Live-Abfrage für Mitarbeiter")
                search_sid_ma = gr.Textbox(label="Studenten-ID eingeben")
                btn_refresh_ma = gr.Button("🔄 Vollständiges Notenblatt laden", variant="secondary")
                noten_anzeige_ma = gr.TextArea(label="Ergebnis aus der Datenbank", lines=18)
                btn_note.click(note_eintragen, inputs=[g_sid, g_cid, g_score, g_date, g_notes], outputs=output_note)
                btn_del_grade.click(note_loeschen, inputs=[delete_gid], outputs=output_del_grade)
                btn_refresh_ma.click(noten_liste_aktualisieren, inputs=[search_sid_ma], outputs=noten_anzeige_ma)
            
            # REITER 5: Reporting
            with gr.Tab("📊 Offizielle Berichte", visible=False) as tab_reports:
                gr.Markdown("### 🖨️ Notenberichte generieren")
                gr.Markdown("Erstellt strukturierte Berichte über das abstrakte ReportGenerator-System.")
                with gr.Row():
                    rep_sid = gr.Textbox(label="Studenten-ID für Bericht eingeben")
                    rep_format = gr.Radio(["Text-Format (.txt)", "CSV-Format (.csv)"], label="Format wählen", value="Text-Format (.txt)")
                    btn_report = gr.Button("Bericht generieren", variant="primary")
                    report_output = gr.TextArea(label="Generierte Ausgabe", lines=15)
                    btn_report.click(frontend_report_erstellen, inputs=[rep_sid, rep_format], outputs=report_output)
            
            # MITARBEITER-LOGIN EVENT
            btn_login.click(mitarbeiter_einloggen, inputs=[user_input, pass_input], outputs=[login_status, tab_verwaltung, tab_noten, tab_reports])
            # MITARBEITER-LOGOUT EVENT
            btn_logout.click(mitarbeiter_ausloggen, inputs=[], outputs=[login_status, tab_verwaltung, tab_noten, tab_reports])

# start the server locally
if __name__ == "__main__":
    dark_mode_js = """function() {document.querySelector('body').classList.add('dark');}"""
    demo.launch(js=dark_mode_js)