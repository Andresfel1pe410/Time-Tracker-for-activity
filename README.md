# Time Tracker Desktop App

Aplicación de escritorio en Python (Tkinter) para el seguimiento de tiempo diario por actividad.

## Features
- Múltiples actividades
- Cronómetro por actividad
- Ventana flotante
- Guardado automático diario
- Persistencia con SQLite

## Instalación
```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python app.py
```
##Build EXE
```bash
pyinstaller --onefile --windowed app.py
```
