document.querySelectorAll('.sort-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
    document.querySelectorAll('.cat-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });

    const isLoggedIn = false; // true/false로 테스트
    function applyAuthState() {
      const promptCard = document.getElementById('loginPromptCard');
      if (isLoggedIn) {
        if (promptCard) promptCard.style.display = 'none';
      } else {
        if (promptCard) promptCard.style.display = 'flex';
      }
    }
    applyAuthState();