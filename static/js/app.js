/**
 * Main Application Controller - Communication Growth Tracker
 */
document.addEventListener('DOMContentLoaded', () => {
  // Global State
  let currentUser = null;
  let speechRecorder = null;
  let currentRecordingDuration = 0;

  // DOM Elements
  const authModal = document.getElementById('authModal');
  const registerForm = document.getElementById('registerForm');
  const loginForm = document.getElementById('loginForm');
  const recordBtn = document.getElementById('recordBtn');
  const recordingTimer = document.getElementById('recordingTimer');
  const liveTranscript = document.getElementById('liveTranscript');
  const analyzeSpeechBtn = document.getElementById('analyzeSpeechBtn');
  const writingInput = document.getElementById('writingInput');
  const analyzeWritingBtn = document.getElementById('analyzeWritingBtn');
  const writingResults = document.getElementById('writingResults');
  const speakingResults = document.getElementById('speakingResults');

  // Navigation Links
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.page-section');

  // Initialize Speech Recorder
  speechRecorder = new SpeechRecorder(
    (transcript) => {
      liveTranscript.value = transcript;
    },
    (seconds) => {
      currentRecordingDuration = seconds;
      const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
      const secs = String(seconds % 60).padStart(2, '0');
      recordingTimer.textContent = `${mins}:${secs}`;
    }
  );

  // Tab Navigation Handler
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('data-target');
      
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');

      sections.forEach(sec => {
        if (sec.id === targetId) {
          sec.style.display = 'block';
        } else {
          sec.style.display = 'none';
        }
      });
    });
  });

  // Auth Modals Toggle
  document.getElementById('openLoginBtn')?.addEventListener('click', () => {
    authModal.classList.add('active');
  });

  document.getElementById('closeAuthModal')?.addEventListener('click', () => {
    authModal.classList.remove('active');
  });

  document.getElementById('toggleAuthMode')?.addEventListener('click', (e) => {
    e.preventDefault();
    if (loginForm.style.display === 'none') {
      loginForm.style.display = 'block';
      registerForm.style.display = 'none';
      document.getElementById('authTitle').textContent = 'Sign In to Your Account';
    } else {
      loginForm.style.display = 'none';
      registerForm.style.display = 'block';
      document.getElementById('authTitle').textContent = 'Create Growth Account';
    }
  });

  // Handle Login Submission
  loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const pass = document.getElementById('loginPassword').value;

    try {
      const res = await ApiClient.login(email, pass);
      localStorage.setItem('token', res.access_token);
      authModal.classList.remove('active');
      loadDashboardData();
    } catch (err) {
      alert('Login failed: ' + err.message);
    }
  });

  // Handle Registration Submission
  registerForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fullName = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const userType = document.getElementById('regUserType').value;
    const profession = document.getElementById('regProfession').value;

    try {
      await ApiClient.register({ full_name: fullName, email, password, user_type: userType, profession });
      // Auto login after registration
      const res = await ApiClient.login(email, password);
      localStorage.setItem('token', res.access_token);
      authModal.classList.remove('active');
      loadDashboardData();
    } catch (err) {
      alert('Registration failed: ' + err.message);
    }
  });

  // Microphone Record Button Click
  recordBtn?.addEventListener('click', () => {
    if (!speechRecorder.isRecording) {
      speechRecorder.start();
      recordBtn.classList.add('recording');
      recordBtn.innerHTML = '⏹';
    } else {
      const { transcript, duration } = speechRecorder.stop();
      recordBtn.classList.remove('recording');
      recordBtn.innerHTML = '🎙';
      currentRecordingDuration = duration;
      if (transcript) {
        liveTranscript.value = transcript;
      }
    }
  });

  // Speech Analysis Trigger
  analyzeSpeechBtn?.addEventListener('click', async () => {
    const text = liveTranscript.value.trim();
    if (!text) {
      alert('Please speak or type a transcript to analyze.');
      return;
    }

    analyzeSpeechBtn.disabled = true;
    analyzeSpeechBtn.textContent = 'Running ML Speech Analysis...';

    try {
      const duration = currentRecordingDuration > 0 ? currentRecordingDuration : Math.max(5, Math.floor(text.split(' ').length * 0.45));
      const res = await ApiClient.analyzeSpeech(text, duration, 'Impromptu Speaking');

      // Display Speaking Analysis Results
      speakingResults.style.display = 'block';
      speakingResults.innerHTML = `
        <div class="glass-panel" style="padding: 1.5rem; margin-top: 1.5rem;">
          <h4 style="font-size: 1.2rem; color: var(--accent-cyan); margin-bottom: 1rem;">Speech Evaluation Report</h4>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
            <div style="background: rgba(15,23,42,0.6); padding: 0.8rem; border-radius: 8px;">
              <div style="font-size: 0.8rem; color: var(--text-muted);">Overall Score</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: var(--primary);">${res.overall_score} / 100</div>
            </div>
            <div style="background: rgba(15,23,42,0.6); padding: 0.8rem; border-radius: 8px;">
              <div style="font-size: 0.8rem; color: var(--text-muted);">Speaking Rate</div>
              <div style="font-size: 1.6rem; font-weight: 800;">${res.wpm} WPM</div>
            </div>
            <div style="background: rgba(15,23,42,0.6); padding: 0.8rem; border-radius: 8px;">
              <div style="font-size: 0.8rem; color: var(--text-muted);">Filler Words</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: ${res.filler_count > 3 ? 'var(--accent-amber)' : 'var(--accent-emerald)'};">${res.filler_count}</div>
            </div>
            <div style="background: rgba(15,23,42,0.6); padding: 0.8rem; border-radius: 8px;">
              <div style="font-size: 0.8rem; color: var(--text-muted);">Primary Weakness</div>
              <div style="font-size: 1.1rem; font-weight: 700; color: var(--accent-rose);">${res.weak_area}</div>
            </div>
          </div>
          <p style="color: var(--text-main); font-size: 0.95rem; line-height: 1.5; margin-bottom: 1rem;">${res.feedback}</p>
          <div class="badge badge-primary">Recommended Practice: ${res.recommended_exercise}</div>
        </div>
      `;

      // Refresh Dashboard Charts
      loadDashboardData();
    } catch (err) {
      alert('Analysis error: ' + err.message);
    } finally {
      analyzeSpeechBtn.disabled = false;
      analyzeSpeechBtn.textContent = 'Analyze Speech Session';
    }
  });

  // Writing Analysis Trigger
  analyzeWritingBtn?.addEventListener('click', async () => {
    const text = writingInput.value.trim();
    if (!text) {
      alert('Please enter text for writing evaluation.');
      return;
    }

    analyzeWritingBtn.disabled = true;
    analyzeWritingBtn.textContent = 'Analyzing Grammar & Tone...';

    try {
      const res = await ApiClient.analyzeWriting(text);

      writingResults.style.display = 'block';
      writingResults.innerHTML = `
        <div class="glass-panel" style="padding: 1.5rem; margin-top: 1.5rem;">
          <h4 style="font-size: 1.2rem; color: var(--primary); margin-bottom: 1rem;">Writing & Grammar Analysis</h4>
          <div style="display: flex; gap: 1.5rem; margin-bottom: 1rem;">
            <span class="badge badge-emerald">Grammar Score: ${res.grammar_score}</span>
            <span class="badge badge-cyan">Vocabulary Score: ${res.vocabulary_score}</span>
            <span class="badge badge-primary">Overall Writing: ${res.overall_score}</span>
          </div>
          
          <div style="margin-bottom: 1rem;">
            <label style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">Polished / Rewritten Version:</label>
            <div style="background: rgba(15,23,42,0.8); border: 1px solid var(--border-highlight); padding: 1rem; border-radius: 8px; font-size: 0.95rem; margin-top: 0.4rem; color: #a5b4fc;">
              ${res.corrected_text}
            </div>
          </div>

          <div style="margin-bottom: 1rem;">
            <label style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">Vocabulary Enhancement Suggestions:</label>
            <ul style="margin-top: 0.4rem; padding-left: 1.2rem; color: var(--text-muted); font-size: 0.9rem;">
              ${res.suggestions.length > 0 ? res.suggestions.map(s => `<li>${s}</li>`).join('') : '<li>Great vocabulary usage! No basic word replacements needed.</li>'}
            </ul>
          </div>
        </div>
      `;
    } catch (err) {
      alert('Writing evaluation error: ' + err.message);
    } finally {
      analyzeWritingBtn.disabled = false;
      analyzeWritingBtn.textContent = 'Evaluate & Polish Text';
    }
  });

  // Load Dashboard Data & Charts
  async function loadDashboardData() {
    try {
      const dash = await ApiClient.getDashboard();
      const recs = await ApiClient.getRecommendations();

      // Update UI elements
      document.getElementById('overallScoreVal').textContent = dash.overall_score;
      document.getElementById('currentLevelVal').textContent = dash.current_level;
      document.getElementById('streakVal').textContent = dash.practice_streak + ' Days';
      document.getElementById('sessionsVal').textContent = dash.sessions_completed;
      document.getElementById('masteredVal').textContent = dash.words_mastered;
      document.getElementById('weakestAreaVal').textContent = dash.weakest_area;
      document.getElementById('nextActivityVal').textContent = dash.recommended_next_activity;

      // Render Charts
      initComponentRadarChart(dash.component_scores);
      initHistoricalTrendChart(dash.recent_trend);

      // Render 7-Day Plan List
      const planContainer = document.getElementById('weeklyPlanContainer');
      if (planContainer && recs.weekly_plan) {
        planContainer.innerHTML = recs.weekly_plan.map(p => `
          <div class="plan-item">
            <div>
              <div class="plan-day">${p.day}</div>
              <div class="plan-title">${p.activity}</div>
            </div>
            <span class="badge badge-cyan">${p.type} (${p.duration})</span>
          </div>
        `).join('');
      }

    } catch (err) {
      console.warn('Dashboard load error:', err);
    }
  }

  // Initial Load
  loadDashboardData();
});
