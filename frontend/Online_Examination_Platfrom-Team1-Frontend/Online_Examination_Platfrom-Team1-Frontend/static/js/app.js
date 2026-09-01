/**
 * MMCOE Online Examination Platform - Shared Application Utilities
 */

// Toast notification trigger
function showToast(message, type = 'info') {
  const toastContainer = document.getElementById('toast-container') || createToastContainer();
  
  const bgClass = type === 'success' ? 'bg-success' : 
                  type === 'danger' ? 'bg-danger' : 
                  type === 'warning' ? 'bg-warning text-dark' : 'bg-primary';

  const toastId = 'toast-' + Date.now();
  const html = `
    <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0 show shadow-sm" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <i class="bi bi-info-circle-fill me-2"></i> ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML('beforeend', html);
  setTimeout(() => {
    const el = document.getElementById(toastId);
    if (el) el.remove();
  }, 4000);
}

function createToastContainer() {
  const div = document.createElement('div');
  div.id = 'toast-container';
  div.className = 'toast-container position-fixed bottom-0 end-0 p-3';
  div.style.zIndex = '9999';
  document.body.appendChild(div);
  return div;
}

// Password visibility toggle helper
function togglePasswordVisibility(inputId, iconId) {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(iconId);
  if (!input) return;
  
  if (input.type === 'password') {
    input.type = 'text';
    if (icon) {
      icon.classList.remove('bi-eye');
      icon.classList.add('bi-eye-slash');
    }
  } else {
    input.type = 'password';
    if (icon) {
      icon.classList.remove('bi-eye-slash');
      icon.classList.add('bi-eye');
    }
  }
}

// Mobile sidebar toggle
function toggleMobileSidebar() {
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.classList.toggle('show');
  }
}

// Dynamic Option Row Adder for Question Creation
function addQuestionOption() {
  const container = document.getElementById('optionsContainer');
  if (!container) return;
  
  const currentCount = container.children.length;
  const optionLetter = String.fromCharCode(65 + currentCount); // A, B, C...
  
  const div = document.createElement('div');
  div.className = 'input-group mb-2 option-row';
  div.id = `option-row-${currentCount}`;
  div.innerHTML = `
    <span class="input-group-text bg-light text-dark font-monospace">${optionLetter}</span>
    <input type="text" class="form-control form-control-custom" placeholder="Option ${optionLetter} text" required>
    <div class="input-group-text bg-light text-dark">
      <input class="form-check-input mt-0" type="checkbox" title="Mark as correct answer">
      <span class="ms-1 small">Correct</span>
    </div>
    <button class="btn btn-outline-danger" type="button" onclick="removeQuestionOption(this)">
      <i class="bi bi-trash"></i>
    </button>
  `;
  container.appendChild(div);
  reindexOptions();
}

function removeQuestionOption(btn) {
  const row = btn.closest('.option-row');
  if (!row) return;
  const container = document.getElementById('optionsContainer');
  if (container.children.length <= 2) {
    showToast('A question must have at least 2 options!', 'warning');
    return;
  }
  row.remove();
  reindexOptions();
}

function reindexOptions() {
  const container = document.getElementById('optionsContainer');
  if (!container) return;
  
  Array.from(container.children).forEach((row, idx) => {
    const letter = String.fromCharCode(65 + idx);
    const span = row.querySelector('.font-monospace');
    if (span) span.textContent = letter;
    const input = row.querySelector('input[type="text"]');
    if (input) input.placeholder = `Option ${letter} text`;
  });
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  // Add mobile menu button to navbar if not exists
  const navbar = document.querySelector('.top-navbar');
  if (navbar && !navbar.querySelector('.mobile-toggle-btn')) {
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-secondary d-lg-none me-2 mobile-toggle-btn';
    btn.innerHTML = '<i class="bi bi-list fs-5"></i>';
    btn.onclick = toggleMobileSidebar;
    navbar.insertBefore(btn, navbar.firstChild);
  }
});
