document.getElementById('btn-register').addEventListener('click', async () => {
  const email = document.getElementById('reg-email').value.trim();
  const nickname = document.getElementById('reg-nickname').value.trim();
  const password = document.getElementById('reg-password').value;
  const confirm = document.getElementById('reg-password-confirm').value;
  const errorEl = document.getElementById('reg-error');

  errorEl.style.display = 'none';

  if (!email || !nickname || !password || !confirm) {
    errorEl.textContent = '모든 항목을 입력해주세요.';
    errorEl.style.display = 'block';
    return;
  }
  if (password !== confirm) {
    errorEl.textContent = '비밀번호가 일치하지 않습니다.';
    errorEl.style.display = 'block';
    return;
  }
  if (password.length < 8) {
    errorEl.textContent = '비밀번호는 8자 이상이어야 합니다.';
    errorEl.style.display = 'block';
    return;
  }
  if (nickname.length < 2 || nickname.length > 10) {
    errorEl.textContent = '닉네임은 2~10자여야 합니다.';
    errorEl.style.display = 'block';
    return;
  }

  const res = await register(email, password, nickname);

  if (res.id) {
    location.href = 'login.html';
  } else {
    errorEl.textContent = res.detail || '회원가입에 실패했습니다.';
    errorEl.style.display = 'block';
  }
});
