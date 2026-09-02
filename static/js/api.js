/**
 * API Client for Communication Growth Tracker
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
      ...options.headers
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: 'Network request failed' }));
      throw new Error(errData.detail || 'API request failed');
    }

    return response.json();
  }

  // Auth Endpoints
  static login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    }).then(res => {
      if (!res.ok) throw new Error('Invalid credentials');
      return res.json();
    });
  }

  static register(data) {
    return this.request('/auth/register', { method: 'POST', body: JSON.stringify(data) });
  }

  static getProfile() {
    return this.request('/profile');
  }

  static updateProfile(data) {
    return this.request('/profile', { method: 'PUT', body: JSON.stringify(data) });
  }

  // Dashboard & Analytics
  static getDashboard() {
    return this.request('/dashboard');
  }

  static getRecommendations() {
    return this.request('/recommendations');
  }

  // Speech Analysis
  static analyzeSpeech(transcript, duration, topic) {
    return this.request('/speaking/analyze', {
      method: 'POST',
      body: JSON.stringify({ transcript, duration, topic })
    });
  }

  // Writing Coach
  static analyzeWriting(text) {
    return this.request('/writing/analyze', {
      method: 'POST',
      body: JSON.stringify({ text })
    });
  }
}
