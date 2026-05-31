const panels = ['posts', 'bookmarks', 'settings'];

function showPanel(name) {
  panels.forEach(p => {
    document.getElementById('panel-' + p).style.display = p === name ? 'block' : 'none';
  });
  document.querySelectorAll('.nav-item').forEach((el, i) => {
    el.classList.toggle('active', ['posts', 'bookmarks', 'settings'][i] === name);
  });
}

function logout() {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  location.href = '../index.html';
}

const user = JSON.parse(localStorage.getItem('user') || 'null');
if (user) {
  document.getElementById('profile-name').textContent = user.nickname;
  document.getElementById('profile-email').textContent = user.email;
  document.getElementById('avatar-initial').textContent = user.nickname[0];
  if (document.getElementById('edit-nickname')) document.getElementById('edit-nickname').value = user.nickname;
}
