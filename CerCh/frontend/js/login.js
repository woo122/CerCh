document.getElementById('btn-login').addEventListener('click', async () => {
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errorEl = document.getElementById('login-error');

  errorEl.style.display = 'none';

  if (!email || !password) {
    errorEl.textContent = '이메일과 비밀번호를 입력해주세요.';
    errorEl.style.display = 'block';
    return;
  }

  const res = await login(email, password);

  if (res.access_token) {
    localStorage.setItem('token', res.access_token);
    localStorage.setItem('user', JSON.stringify(res.user));
    location.href = '../index.html';
  } else {
    errorEl.textContent = res.detail || '로그인에 실패했습니다.';
    errorEl.style.display = 'block';
  }
});

document.getElementById('login-password').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') document.getElementById('btn-login').click();
});
