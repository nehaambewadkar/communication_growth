/**
 * Main Application Controller - Communication Growth Tracker
 * Fully connected to FastAPI Python backend.
 */

// ─────────────────────────────────────────
//  STATE
// ─────────────────────────────────────────
let currentUser    = null;
let speechRecorder = null;
let recordingDuration = 0;

// ─────────────────────────────────────────
//  UTILITY: show / hide page sections
// ─────────────────────────────────────────
function showSection(id) {
  document.querySelectorAll('.page-section').forEach(s => s.style.display = 'none');
  const el = document.getElementById(id);
  if (el) el.style.display = 'block';

  // keep nav highlight in sync
  document.querySelectorAll('.nav-link').forEach(l => {
    l.classList.toggle('active', l.getAttribute('data-target') === id);
  });
}

// ─────────────────────────────────────────
//  UTILITY: topic scenario shortcut
// ─────────────────────────────────────────
function setTopic(text) {
  const ta = document.getElementById('liveTranscript');
  const ti = document.getElementById('speechTopic');
  if (ti) ti.value = text;
  if (ta) ta.focus();
}

// ─────────────────────────────────────────
//  AUTH STATE
// ─────────────────────────────────────────
function applyAuthState(user) {
  currentUser = user;

  const isLoggedIn = !!user;
  const authSection    = document.getElementById('authSection');
  const appContainer   = document.getElementById('appContainer');
  const mainNavbar     = document.getElementById('mainNavbar');
  const navUserBadge   = document.getElementById('navUserBadge');

  if (isLoggedIn) {
    authSection.style.display = 'none';
    appContainer.style.display = 'block';
    mainNavbar.style.display = 'flex';
    navUserBadge.textContent = `👤 ${user.full_name.split(' ')[0]}`;
    showSection('dashboardSection');
    loadDashboardData();
  } else {
    authSection.style.display = 'flex';
    appContainer.style.display = 'none';
    mainNavbar.style.display = 'none';
  }
}

// ─────────────────────────────────────────
//  DASHBOARD: load live data from backend
// ─────────────────────────────────────────
async function loadDashboardData() {
  try {
    const [dash, recs] = await Promise.all([
      ApiClient.getDashboard(),
      ApiClient.getRecommendations()
    ]);

    // Profile header
    document.getElementById('profileNameVal').textContent = currentUser
      ? `${currentUser.full_name}'s Dashboard`
      : 'Communication Dashboard';
    document.getElementById('profileAvatarInitial').textContent = currentUser
      ? currentUser.full_name[0].toUpperCase()
      : 'U';
    document.getElementById('profileProfessionVal').textContent =
      currentUser?.user_type || 'Professional';
    document.getElementById('currentLevelVal').textContent = dash.current_level || 'Intermediate';

    // Metric cards
    document.getElementById('overallScoreVal').textContent = dash.overall_score ?? '—';
    document.getElementById('streakVal').textContent        = (dash.practice_streak ?? '—') + (dash.practice_streak != null ? ' Days' : '');
    document.getElementById('sessionsVal').textContent      = dash.sessions_completed ?? '—';
    document.getElementById('weakestAreaVal').textContent   = dash.weakest_area || '—';

    // Charts
    if (dash.component_scores && Object.keys(dash.component_scores).length > 0) {
      initComponentRadarChart(dash.component_scores);
    }
    if (dash.recent_trend && dash.recent_trend.length > 0) {
      initHistoricalTrendChart(dash.recent_trend);
    }

    // Show/hide the "no sessions" placeholder
    const noMsg = document.getElementById('noSessionsMsg');
    if (noMsg) {
      noMsg.style.display = dash.sessions_completed === 0 ? 'block' : 'none';
    }

    // Weekly plan
    renderWeeklyPlan(recs?.weekly_plan || []);

  } catch (err) {
    console.warn('Dashboard load failed:', err.message);
  }
}

function renderWeeklyPlan(plan) {
  const container = document.getElementById('weeklyPlanContainer');
  if (!container) return;

  if (!plan || plan.length === 0) {
    container.innerHTML = '<p style="color:var(--text-muted); text-align:center;">Complete a session to generate your personalised plan.</p>';
    return;
  }

  container.innerHTML = plan.map((p, i) => `
    <div class="plan-item">
      <div>
        <div class="plan-day">Day ${i + 1} — ${p.day || ''}</div>
        <div class="plan-title">${p.activity}</div>
        ${p.description ? `<div class="plan-desc">${p.description}</div>` : ''}
      </div>
      <span class="badge badge-cyan">${p.type || 'Practice'} ${p.duration ? `(${p.duration})` : ''}</span>
    </div>
  `).join('');
}

// ─────────────────────────────────────────
//  SPEAKING ANALYSIS
// ─────────────────────────────────────────
async function handleSpeechAnalysis() {
  const transcript = document.getElementById('liveTranscript').value.trim();
  const topic      = document.getElementById('speechTopic').value.trim() || 'General Practice';
  const btn        = document.getElementById('analyzeSpeechBtn');
  const resultsDiv = document.getElementById('speakingResults');

  if (!transcript) {
    showToast('Please speak or type a transcript first.', 'error');
    return;
  }

  btn.disabled = true;
  btn.textContent = '⏳ Running ML Analysis...';
  resultsDiv.style.display = 'none';

  try {
    const duration = recordingDuration > 0
      ? recordingDuration
      : Math.max(5, Math.floor(transcript.split(' ').length * 0.45));

    const res = await ApiClient.analyzeSpeech(transcript, duration, topic);

    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
      <div class="glass-panel result-card">
        <h4 class="result-title">📊 Speech Evaluation Report</h4>
        <div class="result-score-grid">
          <div class="result-score-item">
            <div class="rscore-label">Overall Score</div>
            <div class="rscore-value text-gradient">${res.overall_score}<span style="font-size:1rem;">/100</span></div>
          </div>
          <div class="result-score-item">
            <div class="rscore-label">Speaking Rate</div>
            <div class="rscore-value" style="color:var(--accent-cyan);">${res.wpm} <span style="font-size:1rem;">WPM</span></div>
          </div>
          <div class="result-score-item">
            <div class="rscore-label">Filler Words</div>
            <div class="rscore-value" style="color:${res.filler_count > 3 ? 'var(--accent-amber)' : 'var(--accent-emerald)'};">${res.filler_count}</div>
          </div>
          <div class="result-score-item">
            <div class="rscore-label">Weak Area</div>
            <div class="rscore-value" style="font-size:1.2rem; color:var(--accent-rose);">${res.weak_area}</div>
          </div>
        </div>

        <div class="result-scores-row">
          ${renderMiniScore('Fluency',    res.fluency_score)}
          ${renderMiniScore('Grammar',    res.grammar_score)}
          ${renderMiniScore('Vocabulary', res.vocabulary_score)}
          ${renderMiniScore('Clarity',    res.clarity_score)}
          ${renderMiniScore('Confidence', res.confidence_score)}
        </div>

        <div class="result-feedback">
          <strong>📝 AI Feedback:</strong>
          <p>${res.feedback}</p>
        </div>
        <div class="result-rec">
          <span class="badge badge-primary">🎯 Recommended Practice: ${res.recommended_exercise}</span>
        </div>
      </div>`;

    // Refresh dashboard in background
    loadDashboardData();
    showToast('Analysis complete! Dashboard updated.', 'success');
  } catch (err) {
    showToast('Analysis failed: ' + err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '⚡ Analyze with ML Pipeline';
  }
}

function renderMiniScore(label, value) {
  const pct = Math.round(value ?? 0);
  const color = pct >= 75 ? 'var(--accent-emerald)' : pct >= 55 ? 'var(--accent-amber)' : 'var(--accent-rose)';
  return `
    <div class="mini-score">
      <div class="mini-score-label">${label}</div>
      <div class="mini-score-bar">
        <div class="mini-score-fill" style="width:${pct}%; background:${color};"></div>
      </div>
      <div class="mini-score-val" style="color:${color};">${pct}</div>
    </div>`;
}

// ─────────────────────────────────────────
//  WRITING ANALYSIS
// ─────────────────────────────────────────
async function handleWritingAnalysis() {
  const text       = document.getElementById('writingInput').value.trim();
  const btn        = document.getElementById('analyzeWritingBtn');
  const resultsDiv = document.getElementById('writingResults');

  if (!text) {
    showToast('Please enter some text to analyse.', 'error');
    return;
  }

  btn.disabled = true;
  btn.textContent = '⏳ Analysing Grammar & Tone...';
  resultsDiv.style.display = 'none';

  try {
    const res = await ApiClient.analyzeWriting(text);
    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = `
      <div class="glass-panel result-card">
        <h4 class="result-title">✍️ Writing & Grammar Report</h4>
        <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1.25rem;">
          <span class="badge badge-emerald">Grammar: ${res.grammar_score}/100</span>
          <span class="badge badge-cyan">Vocabulary: ${res.vocabulary_score}/100</span>
          <span class="badge badge-primary">Overall: ${res.overall_score}/100</span>
        </div>

        <div class="result-section">
          <label class="result-section-label">✅ Corrected / Polished Version:</label>
          <div class="corrected-text">${res.corrected_text}</div>
        </div>

        ${res.suggestions && res.suggestions.length > 0 ? `
        <div class="result-section">
          <label class="result-section-label">💡 Vocabulary Enhancement Suggestions:</label>
          <ul class="suggestion-list">
            ${res.suggestions.map(s => `<li>${s}</li>`).join('')}
          </ul>
        </div>` : `
        <div class="result-section">
          <label class="result-section-label">💡 Vocabulary:</label>
          <p style="color:var(--accent-emerald); margin-top:0.4rem;">✓ Great vocabulary usage! No basic word replacements needed.</p>
        </div>`}

        <div class="result-feedback">
          <strong>📝 Feedback:</strong>
          <p>${res.feedback || 'Keep practising to improve your writing fluency!'}</p>
        </div>
      </div>`;

    showToast('Writing analysis complete!', 'success');
  } catch (err) {
    showToast('Writing evaluation failed: ' + err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '⚡ Evaluate & Polish Text';
  }
}

// ─────────────────────────────────────────
//  TOAST NOTIFICATIONS
// ─────────────────────────────────────────
function showToast(message, type = 'info') {
  const existing = document.getElementById('appToast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'appToast';
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add('toast-visible'), 50);
  setTimeout(() => {
    toast.classList.remove('toast-visible');
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// ─────────────────────────────────────────
//  INIT ON DOM READY
// ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // --- Navigation ---
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = link.getAttribute('data-target');
      if (target) showSection(target);
    });
  });

  // --- Toggle login / register ---
  document.getElementById('toggleAuthMode')?.addEventListener('click', e => {
    e.preventDefault();
    const lf = document.getElementById('loginForm');
    const rf = document.getElementById('registerForm');
    const toggle = document.getElementById('toggleAuthMode');
    if (rf.style.display === 'none') {
      lf.style.display = 'none';
      rf.style.display = 'block';
      document.getElementById('authTitle').textContent = 'Create Growth Account';
      toggle.textContent = 'Already have an account? Sign in';
    } else {
      lf.style.display = 'block';
      rf.style.display = 'none';
      document.getElementById('authTitle').textContent = 'Sign In to Your Account';
      toggle.textContent = "Don't have an account? Register here";
    }
    document.getElementById('loginError').style.display = 'none';
    document.getElementById('registerError').style.display = 'none';
  });

  // --- Login ---
  document.getElementById('loginForm')?.addEventListener('submit', async e => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const pass  = document.getElementById('loginPassword').value;
    const errEl = document.getElementById('loginError');
    const btn   = document.getElementById('loginSubmitBtn');
    errEl.style.display = 'none';
    btn.disabled = true;
    btn.textContent = 'Signing in...';
    try {
      const res = await ApiClient.login(email, pass);
      localStorage.setItem('token', res.access_token);
      const user = await ApiClient.getMe();
      applyAuthState(user);
      showToast(`Welcome back, ${user.full_name.split(' ')[0]}! 🎉`, 'success');
    } catch (err) {
      errEl.textContent = err.message || 'Invalid email or password.';
      errEl.style.display = 'block';
    } finally {
      btn.disabled = false;
      btn.textContent = 'Login';
    }
  });

  // --- Register ---
  document.getElementById('registerForm')?.addEventListener('submit', async e => {
    e.preventDefault();
    const errEl = document.getElementById('registerError');
    const btn   = document.getElementById('registerSubmitBtn');
    errEl.style.display = 'none';
    btn.disabled = true;
    btn.textContent = 'Creating account...';
    try {
      const payload = {
        full_name:  document.getElementById('regName').value,
        email:      document.getElementById('regEmail').value,
        password:   document.getElementById('regPassword').value,
        user_type:  document.getElementById('regUserType').value,
        profession: document.getElementById('regProfession').value
      };
      await ApiClient.register(payload);
      const res  = await ApiClient.login(payload.email, payload.password);
      localStorage.setItem('token', res.access_token);
      const user = await ApiClient.getMe();
      applyAuthState(user);
      showToast(`Account created! Welcome, ${user.full_name.split(' ')[0]}! 🚀`, 'success');
    } catch (err) {
      errEl.textContent = err.message || 'Registration failed. Please try again.';
      errEl.style.display = 'block';
    } finally {
      btn.disabled = false;
      btn.textContent = 'Create Account';
    }
  });

  // --- Logout ---
  document.getElementById('logoutBtn')?.addEventListener('click', () => {
    localStorage.removeItem('token');
    currentUser = null;
    applyAuthState(null);
    showToast('Logged out successfully.', 'info');
  });

  // --- Speaking Studio ---
  speechRecorder = new SpeechRecorder(
    transcript => { document.getElementById('liveTranscript').value = transcript; },
    seconds => {
      recordingDuration = seconds;
      const m = String(Math.floor(seconds / 60)).padStart(2, '0');
      const s = String(seconds % 60).padStart(2, '0');
      document.getElementById('recordingTimer').textContent = `${m}:${s}`;
    }
  );

  document.getElementById('recordBtn')?.addEventListener('click', () => {
    const btn    = document.getElementById('recordBtn');
    const status = document.getElementById('recordingStatus');
    if (!speechRecorder.isRecording) {
      speechRecorder.start();
      btn.classList.add('recording');
      btn.innerHTML = '⏹';
      status.textContent = 'Recording... click to stop';
      status.style.color = 'var(--accent-rose)';
    } else {
      const { transcript, duration } = speechRecorder.stop();
      btn.classList.remove('recording');
      btn.innerHTML = '🎙';
      status.textContent = 'Click microphone to start recording';
      status.style.color = '';
      recordingDuration = duration;
      if (transcript) document.getElementById('liveTranscript').value = transcript;
    }
  });

  document.getElementById('analyzeSpeechBtn')?.addEventListener('click', handleSpeechAnalysis);
  document.getElementById('analyzeWritingBtn')?.addEventListener('click', handleWritingAnalysis);

  // ─── AUTO-LOGIN if token exists ───
  const savedToken = localStorage.getItem('token');
  if (savedToken) {
    ApiClient.getMe()
      .then(user => applyAuthState(user))
      .catch(() => {
        localStorage.removeItem('token');
        applyAuthState(null);
      });
  } else {
    applyAuthState(null);
  }

});
