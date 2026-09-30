import re

with open('src/components/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add RecordThread class at the top after imports
thread_code = '''
from PySide6.QtCore import QThread, Signal

class RecordThread(QThread):
    finished_recording = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, duration, sample_rate, output_path):
        super().__init__()
        self.duration = duration
        self.sample_rate = sample_rate
        self.output_path = output_path

    def run(self):
        try:
            import sounddevice as sd
            import soundfile as sf
            recording = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
            )
            sd.wait()
            sf.write(str(self.output_path), recording, self.sample_rate)
            self.finished_recording.emit(str(self.output_path))
        except Exception as exc:
            self.error_occurred.emit(str(exc))
'''

# Find the right place for imports and class
import_idx = content.find('from PySide6.QtWidgets')
content = content[:import_idx] + thread_code + '\n' + content[import_idx:]

# Replace _record_audio
record_func = '''    def _record_audio(self) -> None:
        try:
            import sounddevice as sd
            import soundfile as sf
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Recording Error",
                f"Audio recording dependencies are missing.\\n\\n{exc}",
            )
            return

        duration = int(self.duration_spin.value())
        sample_rate = 22050
        record_dir = Path(__file__).resolve().parents[1] / "recordings"
        record_dir.mkdir(parents=True, exist_ok=True)
        output_path = record_dir / "recorded_voice.wav"
        
        # UI Feedback
        for btn in self.findChildren(QPushButton):
            if btn.text() == "Record Audio":
                btn.setEnabled(False)
                btn.setText("Recording...")
                self._current_rec_btn = btn
                break

        self.record_thread = RecordThread(duration, sample_rate, output_path)
        self.record_thread.finished_recording.connect(self._on_record_finished)
        self.record_thread.error_occurred.connect(self._on_record_error)
        self.record_thread.start()

    def _on_record_finished(self, output_path_str: str) -> None:
        if hasattr(self, '_current_rec_btn') and self._current_rec_btn:
            self._current_rec_btn.setEnabled(True)
            self._current_rec_btn.setText("Record Audio")

        output_path = Path(output_path_str)
        self.audio_path = str(output_path)
        self.file_label.setText(output_path.name)
        self._update_quality_view(str(output_path))
        self._refresh_analyze_state()

    def _on_record_error(self, exc: str) -> None:
        if hasattr(self, '_current_rec_btn') and self._current_rec_btn:
            self._current_rec_btn.setEnabled(True)
            self._current_rec_btn.setText("Record Audio")
        QMessageBox.critical(self, "Recording Error", f"Failed to record audio.\\n\\n{exc}")'''

content = re.sub(r'    def _record_audio\(self\) -> None:.*?def _run_analysis', record_func + '\n\n    def _run_analysis', content, flags=re.DOTALL)

with open('src/components/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Patch applied.')
