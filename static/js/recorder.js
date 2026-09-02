/**
 * Audio Recording & Web Speech API Transcription Controller
 */
class SpeechRecorder {
  constructor(onTranscriptUpdate, onTimeUpdate) {
    self.recognition = null;
    self.isRecording = false;
    self.startTime = null;
    self.timerInterval = null;
    self.fullTranscript = '';
    self.onTranscriptUpdate = onTranscriptUpdate;
    self.onTimeUpdate = onTimeUpdate;

    this.initSpeechRecognition();
  }

  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      this.recognition.onresult = (event) => {
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript + ' ';
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        if (final) {
          this.fullTranscript += final;
        }

        if (this.onTranscriptUpdate) {
          this.onTranscriptUpdate(this.fullTranscript + interim);
        }
      };

      this.recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
      };
    } else {
      console.warn('Web Speech API is not supported in this browser.');
    }
  }

  start() {
    this.isRecording = true;
    this.fullTranscript = '';
    this.startTime = Date.now();

    if (this.recognition) {
      try {
        this.recognition.start();
      } catch (e) {
        console.warn('Recognition already started');
      }
    }

    this.timerInterval = setInterval(() => {
      const elapsedSeconds = Math.floor((Date.now() - this.startTime) / 1000);
      if (this.onTimeUpdate) {
        this.onTimeUpdate(elapsedSeconds);
      }
    }, 1000);
  }

  stop() {
    this.isRecording = false;
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
    }
    const totalDurationSeconds = Math.max(1, Math.floor((Date.now() - this.startTime) / 1000));

    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }

    return {
      transcript: this.fullTranscript.trim(),
      duration: totalDurationSeconds
    };
  }
}
