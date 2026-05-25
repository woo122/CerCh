const NAV_ITEMS = [
  { label: '분석',    href: '/index.html' },
  { label: '커뮤니티', href: '/pages/community.html' },
  { label: '일정',    href: '/pages/schedule.html' },
  { label: '마이페이지', href: '/pages/mypage.html' },
];

function renderHeader(activeLabel) {
  const currentUser = JSON.parse(localStorage.getItem('user') || 'null');

  const headerHTML = `
    <header class="header-wrap">
      <div class="header-inner">
        <a href="/index.html" style="text-decoration:none;"><span class="logo">CerCh</span></a>
        <div class="search-wrap">
          <input class="search-input" type="text" placeholder="기술, 자격증, 회사명으로 검색" id="globalSearch" />
          <svg class="search-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="13" y1="13" x2="18" y2="18"/>
          </svg>
        </div>
        <div class="header-actions" id="header-actions">
          ${currentUser
            ? `<span style="font-size:14px;color:#333;align-self:center;">${currentUser.nickname}님</span>
               <button class="btn-outline" onclick="logout()">로그아웃</button>`
            : `<button class="btn-outline" onclick="location.href='/pages/login.html'">로그인</button>
               <button class="btn-outline" onclick="location.href='/pages/register.html'">회원가입</button>`
          }
        </div>
      </div>
    </header>
    <nav class="menubar-wrap">
      <div class="menubar-inner">
        ${NAV_ITEMS.map(item => `
          <a class="menu-item ${item.label !== activeLabel ? 'inactive' : ''}" href="${item.href}">${item.label}</a>
        `).join('')}
      </div>
    </nav>
  `;

  document.body.insertAdjacentHTML('afterbegin', headerHTML);
}

function renderFooter() {
  const footerHTML = `
    <footer class="footer-wrap">
      <div class="footer-inner">
        <div class="footer-top">
          <div class="footer-logo">
            <a href="/index.html" style="text-decoration:none;"><span class="logo">CerCh</span></a>
          </div>
          <p class="footer-desc">기업 채용공고 기반 기술 · 자격증 트렌드를 한눈에 확인하세요.</p>
        </div>
        <div class="footer-links">
          <div class="footer-col">
            <div class="footer-col-title">서비스</div>
            <a href="/index.html">기술 분석</a>
            <a href="/pages/analysis.html">자격증 순위</a>
            <a href="/pages/schedule.html">시험 일정</a>
            <a href="/pages/community.html">커뮤니티</a>
          </div>
          <div class="footer-col">
            <div class="footer-col-title">회사</div>
            <a href="#">소개</a>
            <a href="#">공지사항</a>
            <a href="#">문의하기</a>
          </div>
          <div class="footer-col">
            <div class="footer-col-title">정책</div>
            <a href="#">이용약관</a>
            <a href="#">개인정보처리방침</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 테크스캔. All rights reserved.</span>
      </div>
    </footer>
  `;
  document.body.insertAdjacentHTML('beforeend', footerHTML);
}

function logout() {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  location.href = '/index.html';
}
