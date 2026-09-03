/**
 * Audio Recording & Web Speech API Transcription Controller with Real-time Filler Word Alert Engine
 */
class SpeechRecorder {
  constructor(onTranscriptUpdate, onTimeUpdate, onFillerDetected, onMetricsUpdate) {
    this.recognition = null;
    this.isRecording = false;
    this.startTime = null;
    this.timerInterval = null;
    this.fullTranscript = '';
    this.onTranscriptUpdate = onTranscriptUpdate;
    this.onTimeUpdate = onTimeUpdate;
    this.onFillerDetected = onFillerDetected;
    this.onMetricsUpdate = onMetricsUpdate;

    this.fillerWords = [
      "um", "uh", "like", "actually", "basically", "you know",
      "i mean", "sort of", "kind of", "literally", "honestly",
      "right", "so yeah"
    ];
    this.detectedFillerCount = 0;
    this.lastProcessedLength = 0;

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

        const currentText = (this.fullTranscript + interim).trim();

        // Detect new filler words in incoming stream
        this.scanForLiveFillers(currentText);

        if (this.onTranscriptUpdate) {
          this.onTranscriptUpdate(currentText);
        }

        // Real-time pacing metrics
        if (this.onMetricsUpdate && this.startTime) {
          const elapsedMins = Math.max((Date.now() - this.startTime) / 60000, 0.05);
          const words = currentText.split(/\s+/).filter(w => w.length > 0);
          const wpm = Math.round(words.length / elapsedMins);
          this.onMetricsUpdate({
            wpm: wpm,
            wordCount: words.length,
            fillerCount: this.detectedFillerCount
          });
        }
      };

      this.recognition.onerror = (event) => {
        console.warn('Speech recognition status:', event.error);
        if (event.error === 'network' || event.error === 'no-speech') {
          if (this.isRecording) {
            setTimeout(() => {
              if (this.isRecording) {
                try { this.recognition.start(); } catch (e) {}
              }
            }, 500);
          }
        }
      };

      this.recognition.onend = () => {
        if (this.isRecording) {
          try {
            this.recognition.start();
          } catch (e) {}
        }
      };
    } else {
      console.warn('Web Speech API is not supported in this browser environment.');
    }
  }

  scanForLiveFillers(fullText) {
    const textLower = fullText.toLowerCase();
    const newChunk = textLower.slice(this.lastProcessedLength);

    for (const filler of this.fillerWords) {
      const regex = new RegExp('\\b' + filler + '\\b', 'gi');
      const matches = newChunk.match(regex);
      if (matches && matches.length > 0) {
        this.detectedFillerCount += matches.length;
        if (this.onFillerDetected) {
          this.onFillerDetected(filler, this.detectedFillerCount);
        }
      }
    }
    this.lastProcessedLength = textLower.length;
  }

  start() {
    this.isRecording = true;
    this.fullTranscript = '';
    this.detectedFillerCount = 0;
    this.lastProcessedLength = 0;
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
      duration: totalDurationSeconds,
      fillerCount: this.detectedFillerCount
    };
  }
}
