import os
import tempfile
import subprocess
import whisper
import streamlit as st
from typing import Union


def erstelle_srt(segmente: list[dict]) -> str:
    """
    Erstellt einen SRT-String aus einer Liste von Segmenten.

    Args:
        segmente: Eine Liste von Segment-Dictionaries, die jeweils 'start', 'end' und 'text' enthalten.

    Returns:
        Einen formatierten SRT-String.
    """
    srt_inhalt = ""
    for index, segment in enumerate(segmente, start=1):
        start = segment['start']
        ende = segment['end']
        text = segment['text'].strip()

        start_zeit = sekunden_zu_srt_zeit(start)
        end_zeit = sekunden_zu_srt_zeit(ende)

        srt_inhalt += f"{index}\n{start_zeit} --> {end_zeit}\n{text}\n\n"

    return srt_inhalt


def sekunden_zu_srt_zeit(sekunden: float) -> str:
    """
    Konvertiert Sekunden in das SRT-Zeitformat HH:MM:SS,mmm.

    Args:
        sekunden: Die Zeit in Sekunden.

    Returns:
        Die Zeit im SRT-Format.
    """
    millis = int((sekunden - int(sekunden)) * 1000)
    h = int(sekunden // 3600)
    m = int((sekunden % 3600) // 60)
    s = int(sekunden % 60)
    return f"{h:02}:{m:02}:{s:02},{millis:03}"


def transkribiere_audio_zu_srt(dateipfad: str, model: whisper.Whisper) -> str:
    """
    Transkribiert eine Audiodatei in einen SRT-String.

    Args:
        dateipfad: Der Pfad zur Audiodatei.
        model: Das Whisper-Modell.

    Returns:
        Den transkribierten SRT-String.
    """
    ergebnis = model.transcribe(dateipfad, fp16=False)
    segmente = ergebnis['segments']
    return erstelle_srt(segmente)


def merge_video_mit_srt(video_path: str, srt_path: str, output_path: str) -> tuple[bool, str]:
    """
    Fügt eine SRT-Datei zu einem Video hinzu.

    Args:
        video_path: Der Pfad zur Videodatei.
        srt_path: Der Pfad zur SRT-Datei.
        output_path: Der Pfad für die Ausgabedatei.

    Returns:
        Ein Tupel, das angibt, ob der Vorgang erfolgreich war (True/False) und eine Fehlermeldung (falls vorhanden).
    """
    # Stelle sicher, dass Pfade unter Windows korrekt interpretiert werden
    srt_path_safe = srt_path.replace('\\', '/').replace(':', '\\:')

    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles='{srt_path_safe}'",
        "-c:v", "libx264",  # Videocodec
        "-c:a", "aac",      # Audiocodec
        "-y",                # Überschreiben, falls vorhanden
        output_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def main() -> None:
    """
    Hauptfunktion der Streamlit-Anwendung.
    """
    st.title("🎬 Video mit automatischen Untertiteln")

    model = whisper.load_model("medium")

    audio_datei = st.file_uploader("🔊 Lade deine Audiodatei hoch (optional)", type=["mp3", "wav", "flac"], key="audio")
    srt_datei = st.file_uploader("📄 Lade deine SRT-Datei hoch (optional)", type=["srt"], key="srt")
    video_datei = st.file_uploader("🎞️ Lade dein Video hoch", type=["mp4", "mov", "avi", "mkv"], key="video")

    srt_inhalt = ""

    with tempfile.TemporaryDirectory() as tmpdir:
        if audio_datei:
            audio_path = os.path.join(tmpdir, audio_datei.name)
            with open(audio_path, "wb") as f:
                f.write(audio_datei.read())
            srt_inhalt = transkribiere_audio_zu_srt(audio_path, model)

        if srt_datei:
            srt_inhalt = srt_datei.read().decode('utf-8')

        if srt_inhalt:
            srt_bearbeitet = st.text_area("📝 Bearbeite den SRT-Inhalt nach Bedarf:", srt_inhalt, height=300)

            if video_datei and st.button("🔄 Video mit bearbeiteten Untertiteln zusammenführen"):
                video_path = os.path.join(tmpdir, video_datei.name)
                srt_path = os.path.join(tmpdir, "untertitel.srt")
                output_video_path = os.path.join(tmpdir, "video_mit_untertitel.mp4")

                with open(video_path, "wb") as f:
                    f.write(video_datei.read())

                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(srt_bearbeitet)

                with st.spinner("⏳ Video und Untertitel werden zusammengeführt..."):
                    success, error_message = merge_video_mit_srt(video_path, srt_path, output_video_path)
                    if success:
                        st.success("✅ Video mit Untertiteln erstellt!")
                        with open(output_video_path, "rb") as final_video:
                            st.download_button(
                                label="📥 Video mit Untertiteln herunterladen",
                                data=final_video,
                                file_name="video_mit_untertiteln.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error(f"❌ Fehler beim Zusammenführen:\n{error_message}")



if __name__ == '__main__':
    main()
