document.addEventListener('DOMContentLoaded', () => {
    const list = document.getElementById('grocery-list');
    if (!list) return;
  
    // Strike through checked items
    list.addEventListener('change', (e) => {
      if (e.target.matches('input[type="checkbox"]')) {
        const span = e.target.nextElementSibling;
        span.classList.toggle('line-through');
        span.classList.toggle('text-gray-400');
      }
    });
  
    // Reset button
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        list.querySelectorAll('input[type="checkbox"]').forEach((cb) => {
          cb.checked = false;
          const span = cb.nextElementSibling;
          span.classList.remove('line-through', 'text-gray-400');
        });
      });
    }
  });