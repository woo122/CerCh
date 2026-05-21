const API_BASE = 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  return { 'Authorization': `Bearer ${getToken()}`, 'Content-Type': 'application/json' };
}

async function fetchTechs(filter = '') {
  const url = filter ? `${API_BASE}/api/techs?filter=${filter}` : `${API_BASE}/api/techs`;
  const res = await fetch(url);
  return res.json();
}

async function fetchCerts() {
  const res = await fetch(`${API_BASE}/api/certs`);
  return res.json();
}

async function fetchExams() {
  const res = await fetch(`${API_BASE}/api/exams`);
  return res.json();
}

async function fetchCommunity(page = 1, sort = 'latest') {
  const res = await fetch(`${API_BASE}/api/community?page=${page}&sort=${sort}`);
  return res.json();
}

async function fetchPost(postId) {
  const res = await fetch(`${API_BASE}/api/community/${postId}`);
  return res.json();
}

async function createPost(title, content) {
  const res = await fetch(`${API_BASE}/api/community`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ title, content }),
  });
  return res.json();
}

async function createComment(postId, content) {
  const res = await fetch(`${API_BASE}/api/community/${postId}/comments`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ content }),
  });
  return res.json();
}

async function login(email, password) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

async function register(email, password, nickname) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, nickname }),
  });
  return res.json();
}

async function fetchMyInfo() {
  const res = await fetch(`${API_BASE}/api/auth/me`, { headers: authHeaders() });
  return res.json();
}
