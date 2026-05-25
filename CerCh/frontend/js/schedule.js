/* =============================================
   schedule.js - 시험 일정 페이지 전용 JS
   ============================================= */

// ── 일정 데이터 (백엔드 연동 시 fetch('/api/schedules')로 교체) ──
const scheduleData = [
  { date: '2026-06-02', name: '정보처리기사 실기 접수 마감', type: 'deadline', tag: '국가자격증', color: 'orange' },
  { date: '2026-06-05', name: '네트워크관리사 2급 접수 시작', type: 'apply',    tag: '국가자격증', color: 'green'  },
  { date: '2026-06-07', name: '정보보안기사 필기 시험',       type: 'exam',     tag: '국가자격증', color: 'blue'   },
  { date: '2026-06-14', name: 'AWS SAA 시험',                type: 'exam',     tag: '민간자격증', color: 'orange' },
  { date: '2026-06-15', name: 'SQLD 접수 마감',              type: 'deadline', tag: '민간자격증', color: 'orange' },
  { date: '2026-06-21', name: 'SQLD 시험',                   type: 'exam',     tag: '민간자격증', color: 'blue'   },
  { date: '2026-06-23', name: '리눅스마스터 1급 접수 시작',   type: 'apply',    tag: '민간자격증', color: 'green'  },
  { date: '2026-06-28', name: '리눅스마스터 1급 시험',        type: 'exam',     tag: '민간자격증', color: 'blue'   },
];

const colorMap = { green: 'dot-green', blue: 'dot-blue', orange: 'dot-orange', purple: 'dot-purple' };

// ── 캘린더 ──
let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();

function updateMonthLabel() {
  const months = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'];
  document.getElementById('currentMonth').textContent = `${currentYear}년 ${months[currentMonth]}`;
}

function prevMonth() {
  currentMonth--;
  if (currentMonth < 0) { currentMonth = 11; currentYear--; }
  renderCalendar();
}

function nextMonth() {
  currentMonth++;
  if (currentMonth > 11) { currentMonth = 0; currentYear++; }
  renderCalendar();
}

function renderCalendar() {
  updateMonthLabel();
  const grid = document.getElementById('calGrid');
  grid.innerHTML = '';

  const firstDay   = new Date(currentYear, currentMonth, 1).getDay();
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const daysInPrev  = new Date(currentYear, currentMonth, 0).getDate();
  const today = new Date();
  const totalCells = Math.ceil((firstDay + daysInMonth) / 7) * 7;

  for (let i = 0; i < totalCells; i++) {
    const cell = document.createElement('div');
    cell.className = 'cal-cell';

    let day, month, year, isOther = false;
    if (i < firstDay) {
      day = daysInPrev - firstDay + 1 + i;
      month = currentMonth - 1; year = currentYear;
      if (month < 0) { month = 11; year--; }
      isOther = true;
    } else if (i >= firstDay + daysInMonth) {
      day = i - firstDay - daysInMonth + 1;
      month = currentMonth + 1; year = currentYear;
      if (month > 11) { month = 0; year++; }
      isOther = true;
    } else {
      day = i - firstDay + 1;
      month = currentMonth; year = currentYear;
    }

    if (isOther) cell.classList.add('other-month');
    const dayOfWeek = i % 7;
    if (dayOfWeek === 0) cell.classList.add('sunday');
    if (dayOfWeek === 6) cell.classList.add('saturday');

    const isToday = !isOther && year === today.getFullYear() && month === today.getMonth() && day === today.getDate();
    if (isToday) cell.classList.add('today');

    const dateEl = document.createElement('div');
    dateEl.className = 'cal-date';
    dateEl.textContent = day;
    cell.appendChild(dateEl);

    const dotWrap = document.createElement('div');
    dotWrap.className = 'cal-dot-wrap';

    if (!isOther) {
      const dateStr = `${year}-${String(month + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
      const events = scheduleData.filter(e => e.date === dateStr);
      events.slice(0, 2).forEach(ev => {
        const dot = document.createElement('div');
        dot.className = `cal-dot ${colorMap[ev.color]}`;
        dot.textContent = ev.name;
        dotWrap.appendChild(dot);
      });
      if (events.length > 2) {
        const more = document.createElement('div');
        more.className = 'cal-dot';
        more.style.cssText = 'color:#aaa; font-size:10px; padding: 1px 6px;';
        more.textContent = `+${events.length - 2}개 더`;
        dotWrap.appendChild(more);
      }
    }
    cell.appendChild(dotWrap);
    grid.appendChild(cell);
  }
}

// ── 주요 일정 리스트 ──
function renderScheduleList() {
  const list = document.getElementById('scheduleList');
  list.innerHTML = '';
  const today = new Date(); today.setHours(0,0,0,0);

  scheduleData.forEach(item => {
    const d = new Date(item.date); d.setHours(0,0,0,0);
    const months = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월'];
    const typeLabel = item.type === 'exam' ? '시험일' : item.type === 'deadline' ? '마감' : '접수 시작';
    const tagBg    = item.color === 'green' ? '#dcfce7' : item.color === 'blue' ? '#dbeafe' : '#ffedd5';
    const tagColor = item.color === 'green' ? '#15803d' : item.color === 'blue' ? '#1d4ed8' : '#c2410c';

    const diff = Math.round((d - today) / (1000 * 60 * 60 * 24));
    let ddayHtml = '';
    if (diff >= 0) {
      const ddayText  = diff === 0 ? 'D-day' : `D-${diff}`;
      const ddayColor = diff <= 7 ? '#ef4444' : diff <= 14 ? '#f59e0b' : '#22c55e';
      ddayHtml = `<span style="font-size:12px;font-weight:700;color:${ddayColor};margin-left:auto;white-space:nowrap;">${ddayText}</span>`;
    }

    list.innerHTML += `
      <div class="schedule-item">
        <div class="schedule-date-badge">
          <div class="month">${months[d.getMonth()]}</div>
          <div class="day">${d.getDate()}</div>
        </div>
        <div class="schedule-info">
          <div class="schedule-name" style="display:flex;align-items:center;gap:6px;">
            <span>${item.name}</span>${ddayHtml}
          </div>
          <div class="schedule-meta">${typeLabel}</div>
          <span class="schedule-tag" style="background:${tagBg};color:${tagColor}">${item.tag}</span>
        </div>
      </div>`;
  });
}

// ── 필터 칩 ──
function filterChip(el) {
  const group = el.parentElement;
  const chips = Array.from(group.querySelectorAll('.chip'));
  const allBtn = chips[0]; // 첫 번째가 항상 '전체'

  if (el === allBtn) {
    // 전체 버튼 클릭 → 전체 활성 또는 전체 비활성 토글
    const allActive = chips.every(c => c.classList.contains('active'));
    if (allActive) {
      chips.forEach(c => c.classList.remove('active'));
    } else {
      chips.forEach(c => c.classList.add('active'));
    }
  } else {
    // 개별 버튼 클릭 → 해당 버튼 토글
    el.classList.toggle('active');

    // 전체가 다 켜지면 전체 버튼도 활성
    const nonAllChips = chips.slice(1);
    if (nonAllChips.every(c => c.classList.contains('active'))) {
      allBtn.classList.add('active');
    } else {
      allBtn.classList.remove('active');
    }
  }
}

// ── 저장한 자격증 ──
const certCatalog = [
  { id: 1, name: '정보처리기사',    sub: '국가기술자격 · 개발',  icon: '💻', bg: '#dbeafe' },
  { id: 2, name: 'AWS SAA',        sub: '민간자격증 · 클라우드', icon: '☁️', bg: '#e0f2fe' },
  { id: 3, name: 'SQLD',           sub: '민간자격증 · 데이터',   icon: '🗄️', bg: '#dcfce7' },
  { id: 4, name: '정보보안기사',    sub: '국가기술자격 · 보안',   icon: '🔒', bg: '#ede9fe' },
  { id: 5, name: '리눅스마스터 1급', sub: '민간자격증 · 시스템',  icon: '🐧', bg: '#ffedd5' },
];
let savedCerts = [1, 2, 3];

function renderSavedCerts() {
  const list  = document.getElementById('savedCertList');
  const badge = document.getElementById('savedBadge');
  if (!list || !badge) return;
  badge.textContent = savedCerts.length + '개';
  if (savedCerts.length === 0) {
    list.innerHTML = `<div class="saved-cert-empty">🔖<p>저장한 자격증이 없어요</p></div>`;
    return;
  }
  list.innerHTML = '';
  savedCerts.forEach(id => {
    const cert = certCatalog.find(c => c.id === id);
    if (!cert) return;
    list.innerHTML += `
      <div class="saved-cert-item">
        <div class="saved-cert-icon" style="background:${cert.bg}">${cert.icon}</div>
        <div class="saved-cert-info">
          <div class="saved-cert-name">${cert.name}</div>
          <div class="saved-cert-sub">${cert.sub}</div>
        </div>
        <button class="saved-cert-remove" onclick="removeCert(${cert.id})" title="삭제">✕</button>
      </div>`;
  });
}

function removeCert(id) {
  savedCerts = savedCerts.filter(c => c !== id);
  renderSavedCerts();
}

function addCertPrompt() {
  const available = certCatalog.filter(c => !savedCerts.includes(c.id));
  if (available.length === 0) { alert('저장 가능한 자격증이 없습니다.'); return; }
  const names = available.map((c, i) => `${i + 1}. ${c.name}`).join('\n');
  const input = prompt(`추가할 자격증 번호를 입력하세요:\n\n${names}`);
  const idx = parseInt(input) - 1;
  if (!isNaN(idx) && available[idx]) {
    savedCerts.push(available[idx].id);
    renderSavedCerts();
  }
}

// ── 로그인 상태 ──
// 실제 연동 시 → const res = await fetch('/api/auth/me'); const isLoggedIn = res.ok;
const isLoggedIn = false;

function applyAuthState() {
  const savedCard  = document.getElementById('savedCertCard');
  const promptCard = document.getElementById('loginPromptCard');
  if (isLoggedIn) {
    if (savedCard)  savedCard.style.display  = 'block';
    if (promptCard) promptCard.style.display = 'none';
  } else {
    if (savedCard)  savedCard.style.display  = 'none';
    if (promptCard) promptCard.style.display = 'flex';
  }
}

// ── 초기화 ──
document.addEventListener('DOMContentLoaded', () => {
  renderCalendar();
  renderScheduleList();
  renderSavedCerts();
  applyAuthState();
});
