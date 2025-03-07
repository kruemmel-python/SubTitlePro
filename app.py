import os
import tempfile
import subprocess
import logging
import whisper
import streamlit as st
from typing import Union

# Logging konfigurieren für bessere Fehleranalyse
logging.basicConfig(level=logging.INFO)

def erstelle_srt(segmente: list[dict]) -> str:
    """Erstellt SRT-Dateiinhalt aus Whisper-Segmenten."""
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
    """Konvertiert Sekunden in SRT-Zeitformat (HH:MM:SS,mmm)."""
    millis = int((sekunden - int(sekunden)) * 1000)
    h = int(sekunden // 3600)
    m = int((sekunden % 3600) // 60)
    s = int(sekunden % 60)
    return f"{h:02}:{m:02}:{s:02},{millis:03}"


def transkribiere_audio_zu_srt(dateipfad: str, model: whisper.Whisper, sprache: Union[str, None]) -> str:
    """Transkribiert eine Audiodatei mit Whisper und erstellt SRT-Inhalt."""
    ergebnis = model.transcribe(dateipfad, fp16=False, language=sprache)
    segmente = ergebnis['segments']
    return erstelle_srt(segmente)


def merge_video_mit_srt(video_path: str, srt_path: str, output_path: str) -> tuple[bool, str]:
    """Fügt SRT-Untertitel zu einem Video mithilfe von FFmpeg hinzu.

    Anpassungsmöglichkeiten:
    - Videoformat ändern: Unterstützte Formate umfassen mp4, mov, avi, mkv.
    - Videocodecs ändern: z.B. libx264 (H.264, kompatibel und weit verbreitet), libx265 (HEVC, bessere Kompression), mpeg4.
    - Audiocodecs ändern: z.B. aac (kompatibel und gut unterstützt), mp3, ac3, opus.
    - Lautstärke anpassen: Mithilfe zusätzlicher FFmpeg-Filter, z.B. -af "volume=1.5" für 150% Lautstärke.
    - Weitere Anpassungen möglich wie Bitrate, Framerate, Auflösung über entsprechende FFmpeg-Parameter.

      Beispiele:
      - Bitrate einstellen: '-b:v 1M' für 1 Megabit pro Sekunde
      - Framerate ändern: '-r 30' für 30 Bilder pro Sekunde
      - Auflösung anpassen: '-s 1280x720' für HD-Auflösung (720p)

    Wichtige FFmpeg-Parameter:
    - -i: Pfad zur Eingabedatei (Video).
    - -vf subtitles: Filter zum Einbetten der Untertitel.
    - -c:v: Auswahl des Videocodecs.
    - -c:a: Auswahl des Audiocodecs ("copy" kopiert Audiostream unverändert).
    - -y: Überschreiben der Ausgabedatei ohne Rückfrage.

    Args:
        video_path (str): Pfad zum Originalvideo.
        srt_path (str): Pfad zur SRT-Untertiteldatei.
        output_path (str): Zielpfad für das generierte Video.

    Returns:
        tuple[bool, str]: (True, Fehlermeldung falls erfolgreich, sonst False und Fehlermeldung)
    """
    srt_path_safe = srt_path.replace('\\', '/').replace(':', '\\:')

    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles='{srt_path_safe}'",
        "-c:v", "libx264",  # Standardmäßiger Videocodec (H.264)
        "-c:a", "copy",     # Audiostream kopieren, keine Neukodierung
        "-y",                # Überschreibt bestehende Dateien ohne Nachfrage
        output_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        logging.error(f"FFmpeg Fehler: {result.stderr}")  # Detaillierte Fehlermeldung bei Problemen

    return result.returncode == 0, result.stderr


def validate_srt(content: str) -> bool:
    """Überprüft die Gültigkeit des SRT-Inhalts."""
    try:
        entries = content.strip().split("\n\n")
        for entry in entries:
            lines = entry.split("\n")
            if len(lines) < 3:
                return False
            if "-->" not in lines[1]:
                return False
        return True
    except:
        return False


def main() -> None:
    """Hauptfunktion der Streamlit-Anwendung."""
    st.title("🎬 Video mit automatischen Untertiteln")
    st.write("Diese Anwendung ermöglicht es dir, Untertitel aus einer Audiodatei zu generieren oder eine vorhandene SRT-Datei zu verwenden, um sie in dein Video einzubetten.")

    model_option = st.selectbox(
        "🔍 Wähle das Whisper-Modell:",
        ["tiny", "base", "small", "medium", "large"],
        index=3 # Standard: "medium"
    )
    model = whisper.load_model(model_option)

    sprache = st.selectbox(
        "🌎 Wähle die Sprache des Videos:",
        ["auto", "de", "en", "fr", "es", "it", "ru"],
        index=0
    )


    audio_datei = st.file_uploader("🔊 Lade deine Audiodatei hoch (optional)", type=["mp3", "wav", "flac"], key="audio")
    srt_datei = st.file_uploader("📄 Lade deine SRT-Datei hoch (optional)", type=["srt"], key="srt")
    video_datei = st.file_uploader("🎞️ Lade dein Video hoch", type=["mp4", "mov", "avi", "mkv"], key="video")

    srt_inhalt = ""

    with tempfile.TemporaryDirectory() as tmpdir:
        if audio_datei:
            audio_path = os.path.join(tmpdir, audio_datei.name)
            with open(audio_path, "wb") as f:
                f.write(audio_datei.read())
            srt_inhalt = transkribiere_audio_zu_srt(audio_path, model, sprache if sprache != "auto" else None)

        if srt_datei:
            srt_inhalt = srt_datei.read().decode('utf-8')
            if not validate_srt(srt_inhalt):
                st.error("⚠️ Fehler: Die hochgeladene SRT-Datei ist ungültig!")
                return

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
