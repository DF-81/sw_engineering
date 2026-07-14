import gradio as gr
import sqlite3
from pathlib import Path
from notenverwaltung.student import Student
from notenverwaltung.course import Course
from notenverwaltung.grade import Grade
from notenverwaltung.database import GradeDatabase
from notenverwaltung.reports import TextReportGenerator, CsvReportGenerator
from notenverwaltung.database import GradeDatabase

DB_PATH = "noten.db"
db = GradeDatabase(DB_PATH)
db.create_schema()

# --- Login-Validation for employees ---
def mitarbeiter_einloggen(benutzername, passwort):
    if benutzername == "admin" and passwort == "geheim123":
        return (
            "🔓 Login erfolgreich! Die Mitarbeiter-Bereiche wurden freigeschaltet.", 
            gr.update(visible=True), 
            gr.update(visible=True),
            gr.update(visible=True)
        )
    else:
        return "❌ Fehler: Ungültige Zugangsdaten. Zugriff verweigert.", gr.update(visible=False), gr.update(visible=False)

# Logout for employees
def mitarbeiter_ausloggen():
    return (
        "🔒 Erfolgreich abgemeldet. Die Bereiche wurden wieder gesperrt.", 
        gr.update(visible=False), 
        gr.update(visible=False),
        gr.update(visible=False)  # Sperrt auch den Report-Tab wieder
    )

# --- BACKEND LOGIC ---
def note_loeschen(note_id):
    if not note_id:
        return "❌ Fehler: Bitte eine Noten-ID eingeben!"
    try:
        with db._conn:
            cursor = db._conn.cursor()
            cursor.execute("SELECT * FROM grades WHERE id = ?;", (int(note_id),))
            if not cursor.fetchone():
                return f"❌ Fehler: Keine Note mit der ID '{note_id}' gefunden."
            
            cursor.execute("DELETE FROM grades WHERE id = ?;", (int(note_id),))
            db._conn.commit()
        return f"🗑️ Erfolg: Kurs-Note mit ID {note_id} wurde für den Studenten entfernt!"
    except ValueError:
        return "❌ Fehler: Die Noten-ID muss eine Zahl sein!"
    except Exception as e:
        return f"❌ Fehler beim Löschen: {str(e)}"

def noten_liste_aktualisieren(s_id):
    if not s_id:
        return "Bitte geben Sie links eine Studenten-ID ein, um dessen Noten zu laden."
    
    s_id_clean = s_id.strip().upper()

    cursor = db._conn.cursor()
    query = """
        SELECT g.id AS grade_id, g.score, g.date, g.notes,
               s.student_id, s.first_name, s.last_name, s.email,
               c.course_id, c.name AS course_name, c.max_grade, c.passing_grade
        FROM grades g
        JOIN students s ON g.student_id = s.student_id
        JOIN courses c ON g.course_id = c.course_id
        WHERE g.student_id = ?;
    """
    cursor.execute(query, (s_id_clean,))
    rows = cursor.fetchall()
    
    if not rows:
        return f"Keine Noten für Student ID '{s_id_clean}' in der Datenbank gefunden."
    
    text = f"📋 Notenblatt für Student-ID: {s_id_clean}\n"
    text += "="*50 + "\n"
    for row in rows:
        status = "PASSED" if row["score"] >= row["passing_grade"] else "FAILED"
        pct = (row["score"] / row["max_grade"]) * 100.0
        letter = "A" if pct >= 90 else "B" if pct >= 80 else "C" if pct >= 70 else "D" if pct >= 60 else "F"
        
        text += f"🆔 GRADE-ID: {row['grade_id']}\n"
        text += f"📘 Kurs: {row['course_name']} ({row['course_id']})\n"
        text += f"   Punkte: {row['score']}/{row['max_grade']} ({letter}) -> [{status}]\n"
        if row["notes"]:
            text += f"   Notiz: {row['notes']}\n"
        text += f"   Datum: {row['date']}\n"
        text += "-"*50 + "\n"
    return text

def student_hinzufuegen(s_id, vorname, nachname, email):
    try:
        if not s_id or not vorname or not nachname or not email:
            return "❌ Fehler: Alle Felder müssen ausgefüllt sein!"
        
        s_id_clean = s_id.strip().upper()
        neuer_student = Student(s_id_clean, vorname.strip(), nachname.strip(), email.strip())
        db.add_student(neuer_student)
        return f"✅ Erfolg: Student {vorname} {nachname} ({s_id_clean}) gespeichert!"
    except ValueError as e: return f"❌ Fehler: {str(e)}"

def student_loeschen(s_id):
    if not s_id: return "❌ Fehler: Bitte eine Studenten-ID eingeben!"

    s_id_clean = s_id.strip().upper() # add strip() to remove whitespace and upper() to standardize the ID format
    try:
        with db._conn:
            cursor = db._conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?;", (s_id_clean,))
            if not cursor.fetchone():
                return f"❌ Fehler: Student '{s_id_clean}' existiert nicht."
            
            cursor.execute("DELETE FROM students WHERE student_id = ?;", (s_id_clean,))
            db._conn.commit()
        return f"🗑️ Erfolg: Student '{s_id_clean}' komplett gelöscht!"
    except Exception as e: return f"❌ Fehler: {str(e)}"

def kurs_hinzufuegen(c_id, name, max_g, pass_g):
    try:
        if not c_id or not name:
            return "❌ Fehler: ID und Name müssen ausgefüllt sein!"
        
        c_id_clean = c_id.strip().upper()
        neuer_kurs = Course(c_id_clean, name.strip(), float(max_g), float(pass_g)) 
        db.add_course(neuer_kurs)
        return f"✅ Erfolg: Kurs '{name}' ({c_id_clean}) gespeichert!"
    except ValueError as e: return f"❌ Fehler: {str(e)}"

def note_eintragen(s_id, c_id, score, datum, notiz):
    try:
        s_id_clean = s_id.strip().upper()
        c_id_clean = c_id.strip().upper()

        student_obj = db.get_student(s_id_clean)
        course_obj = db.get_course(c_id_clean)
        if not student_obj:
            return f"❌ Fehler: Student '{s_id_clean}' existiert nicht!"
        if not course_obj:
            return f"❌ Fehler: Kurs '{c_id_clean}' existiert nicht!"
        
        neue_note = Grade(student=student_obj, course=course_obj, score=float(score), date=datum.strip(), notes=notiz.strip())
        db.record_grade(neue_note)
        return f"✅ Erfolg: Note für {student_obj.full_name} verbucht!"
    except ValueError as e:
        return f"❌ Fehler: {str(e)}"

# --- GRAPHICAL INTERFACE DESIGN ---
with gr.Blocks(title="Persistent Grade Tracker") as demo:
    gr.Markdown("# 🗄️ Student Grade Tracker (SQLite)")
    gr.Markdown("Diese Oberfläche ist live mit Ihrer echten SQL-Datenbank gekoppelt. Alle Daten bleiben dauerhaft erhalten.")

    # Tab: Public Section
    with gr.Tab("🔍 Mein Notenblatt (Öffentlich)"):
        gr.Markdown("### Schau dir deine Noten an")
        search_sid = gr.Textbox(label="Gib deine Studenten-ID ein (z.B. S123)")
        btn_refresh = gr.Button("🔄 Noten abrufen", variant="primary")
        noten_anzeige = gr.TextArea(label="Deine Noten", lines=15)
        
        btn_refresh.click(noten_liste_aktualisieren, inputs=[search_sid], outputs=noten_anzeige)

    # Tab: Login & Logout for employees
    with gr.Tab("🔐 Mitarbeiter-Login"):
        gr.Markdown("### Interner Bereich für Lehrkräfte und Verwaltung")
        with gr.Row():
            user_input = gr.Textbox(label="Benutzername")
            pass_input = gr.Textbox(label="Passwort", type="password")
        
        with gr.Row():
            btn_login = gr.Button("Anmelden", variant="secondary")
            btn_logout = gr.Button("Abmelden", variant="stop")

        login_status = gr.Textbox(label="Status")

    # Tab: Invisible area until Login
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

    # Tab: Grade organization (Protected Grade Management - Invisible until Login)
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
                btn_note.click(note_eintragen, inputs=[g_sid, g_cid, g_score, g_date, g_notes],
                outputs=output_note)
                btn_del_grade.click(note_loeschen, inputs=[delete_gid], outputs=output_del_grade)
                btn_refresh_ma.click(noten_liste_aktualisieren, inputs=[search_sid_ma],
                outputs=noten_anzeige_ma)

    # Tab: Reporting (Invisible until Login)
        with gr.Tab("📊 Offizielle Berichte", visible=False) as tab_reports:
            gr.Markdown("### 🖨️ Notenberichte generieren")
            gr.Markdown("Erstellt strukturierte Berichte über das abstrakte ReportGenerator-System.")
            
            with gr.Row():
                rep_sid = gr.Textbox(label="Studenten-ID für Bericht eingeben")
                rep_format = gr.Radio(["Text-Format (.txt)", "CSV-Format (.csv)"], label="Format wählen", value="Text-Format (.txt)")
            btn_report = gr.Button("Bericht generieren", variant="primary")
            report_output = gr.TextArea(label="Generierte Ausgabe", lines=12)
            
            
            # Generator Logic for switch-case-t (Polymorphismus)
            def frontend_report_erstellen(student_id, datei_format):
                # Because of using SQLite, loading Data for Gradebook again
                from notenverwaltung.reports import TextReportGenerator, CsvReportGenerator
                from notenverwaltung.gradebook import GradeBook
            
                # Wir bauen temporär ein GradeBook auf, das der Generator versteht
                temp_gb = GradeBook()
                s_obj = db.get_student(student_id)
                if not s_obj:
                    return f"❌ Fehler: Student '{student_id}' nicht in der Datenbank gefunden."
            
                temp_gb.add_student(s_obj)
                for g in db.get_student_grades(student_id.strip().upper()):
                    temp_gb.add_course(g.course)
                    temp_gb.grades.append(g)
            
                # Hier greift die abstrakte Magie: Wir wählen einfach den Generator aus
                if "Text" in datei_format:
                    generator = TextReportGenerator()
                else:
                    generator = CsvReportGenerator()
                
                # Der Aufruf bleibt für beide Formate absolut identisch!
                return generator.generate_student_report(student_id.strip().upper(), temp_gb)

            btn_report.click(frontend_report_erstellen, inputs=[rep_sid, rep_format], outputs=report_output)
            

            # Employee login event to show the protected tabs
            btn_login.click(
            mitarbeiter_einloggen,
            inputs=[user_input, pass_input],
            outputs=[login_status, tab_verwaltung, tab_noten, tab_reports])

            # Employee logout event to hide the protected tabs again
            btn_logout.click(
            mitarbeiter_ausloggen,
            inputs=[],
            outputs=[login_status, tab_verwaltung, tab_noten, tab_reports]) # Sperrt die Tabs live wieder!

# start the server locally
if __name__ == "__main__":
    # Wir starten die App ganz normal ohne fehlerhafte Argumente.
    # Über das kleine 'js'-Skript sagen wir dem Browser beim Laden, 
    # dass er sofort in den dunklen Modus umschalten soll.
    dark_mode_js = """
    function() {
        document.querySelector('body').classList.add('dark');
    }
    """
    demo.launch(js=dark_mode_js)
