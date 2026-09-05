/**
 * API Client - Communication Growth Tracker
 * Connects the frontend to the FastAPI Python backend.
 */
const API_BASE = '/api';

class ApiClient {

  static getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  static async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeader(),
      ...(options.headers || {})
    };
    const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: 'Network request failed' }));
      throw new Error(errData.detail || `HTTP ${response.status}`);
    }
    return response.json();
  }

  // ── Auth ──────────────────────────────────────────────
  static login(email, password) {
    const body = new URLSearchParams({ username: email, password });
    return fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body
    }).then(async res => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
        throw new Error(err.detail || 'Invalid credentials');
      }
      return res.json();
    });
  }

  static register(data) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  /** Get current logged-in user info */
  static getMe() {
    return this.request('/auth/me');
  }

  // ── Dashboard & Analytics ────────────────────────────
  static getDashboard() {
    return this.request('/dashboard');
  }

  static getRecommendations() {
    return this.request('/recommendations');
  }

  // ── Speaking ─────────────────────────────────────────
  static analyzeSpeech(transcript, duration, topic) {
    return this.request('/speaking/analyze', {
      method: 'POST',
      body: JSON.stringify({ transcript, duration, topic })
    });
  }

  static getSpeakingHistory() {
    return this.request('/speaking/history');
  }

  // ── Writing ──────────────────────────────────────────
  static analyzeWriting(text) {
    return this.request('/writing/analyze', {
      method: 'POST',
      body: JSON.stringify({ text })
    });
  }

  static getWritingHistory() {
    return this.request('/writing/history');
  }
}
