document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('studentRegistrationForm');
  if (!form) return;
  const departmentSelect = document.getElementById('departmentId');
  apiRequest('/auth/departments').then(({ data = [] }) => {
    departmentSelect.innerHTML = '<option value="">Select department</option>' + data.map(d => `<option value="${d.department_id}">${authEscape(d.department_code)} — ${authEscape(d.department_name)}</option>`).join('');
  }).catch(error => { departmentSelect.innerHTML = '<option value="">Could not load departments</option>'; showToast(error.message, 'danger'); });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('[type="submit"]');
    button.disabled = true;
    try {
      await apiRequest('/auth/register', { method: 'POST', body: JSON.stringify({
        first_name: document.getElementById('firstName').value.trim(),
        last_name: document.getElementById('lastName').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        password: document.getElementById('password').value,
        department_id: Number(departmentSelect.value),
        roll_number: document.getElementById('rollNumber').value.trim(),
        enrollment_number: document.getElementById('enrollmentNumber').value.trim(),
        year: Number(document.getElementById('studentYear').value),
        semester: Number(document.getElementById('studentSemester').value)
      }) });
      showToast('Account created. Sign in to continue.', 'success');
      window.location.href = '/auth/login.html';
    } catch (error) { button.disabled = false; showToast(error.message, 'danger'); }
  });
});

function authEscape(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
