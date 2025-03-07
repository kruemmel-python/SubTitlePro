# 🎬 SubTitlePro: Automatische Video-Untertitel

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.22.0+-orange)](https://streamlit.io/)
[![Whisper](https://img.shields.io/badge/Whisper-OpenAI-red)](https://openai.com/research/whisper)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-4.4+-green)](https://ffmpeg.org/)


SubTitlePro ist eine Streamlit-Anwendung, die automatisch Untertitel für Videos generiert und diese direkt in das Video einbettet.  Sie nutzt die fortschrittliche Spracherkennungstechnologie von OpenAI Whisper, um präzise Transkripte zu erstellen, und FFmpeg, um diese nahtlos in Ihre Videos zu integrieren.

## ✨ Hauptmerkmale

* **Automatische Transkription:**  Lade einfach deine Audio- oder Videodatei hoch und SubTitleSync generiert automatisch Untertitel mithilfe von Whisper.
* **Manuelle Bearbeitung:**  Überprüfe und bearbeite die generierten Untertitel direkt in der Anwendung, um maximale Genauigkeit zu gewährleisten.
* **SRT-Unterstützung:** Lade bestehende SRT-Dateien hoch, um sie zu bearbeiten oder mit deinem Video zu synchronisieren.
* **Nahtlose Integration:**  Die Untertitel werden direkt in das Video eingebettet, sodass du eine einzige, einfach teilbare Datei erhältst.
* **Benutzerfreundliche Oberfläche:**  Die intuitive Streamlit-Oberfläche macht die Erstellung von Videos mit Untertiteln zum Kinderspiel.
* **Lokale Verarbeitung:** Die Verarbeitung findet lokal auf deinem Rechner statt, wodurch Datenschutz und Geschwindigkeit optimiert werden.


## 🚀 Schnellstart

1. **Installation:**
   ```bash
   pip install streamlit whisper ffmpeg-python
   ```

2. **Ausführen:**
   ```bash
   streamlit run app.py
   ```
   Ersetze `app.py` mit dem Namen deiner Python-Datei (z.B. `app.py`).

3. **Anwendung nutzen:**
   * Lade deine Video-Datei hoch.
   * Optional: Lade eine Audio-Datei hoch oder eine SRT-Datei, um bereits vorhandene Untertitel zu verwenden oder zu bearbeiten.
   * Bearbeite die Untertitel im Textfeld, falls erforderlich.
   * Klicke auf "Video mit bearbeiteten Untertiteln zusammenführen".
   * Lade das fertige Video mit eingebetteten Untertiteln herunter.


## 💻 Unterstützte Formate

* **Audio:** MP3, WAV, FLAC
* **Video:** MP4, MOV, AVI, MKV
* **Untertitel:** SRT


## 👨‍💻 Entwickler

* Ralf Krümmel - [ralf.kruemmel+python@outlook.de](mailto:ralf.kruemmel+python@outlook.de)
* GitHub: [kruemmel-python](https://github.com/kruemmel-python)


## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.


## 🤝 Beitrag leisten

Beiträge sind willkommen! Bitte forke das Repository und erstelle einen Pull-Request mit deinen Änderungen.


## 🙏 Danksagung

Ein besonderer Dank geht an das OpenAI-Team für die Entwicklung von Whisper und an die FFmpeg-Community.
