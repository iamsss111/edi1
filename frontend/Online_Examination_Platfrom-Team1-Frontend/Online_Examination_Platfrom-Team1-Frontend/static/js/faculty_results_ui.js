document.addEventListener('DOMContentLoaded', initializeBulkResultPublishing);

async function initializeBulkResultPublishing() {
  const select = document.getElementById('publishExamSelect');
  const form = document.getElementById('bulkPublishForm');
  if (!select || !form) return;
  try {
    const { data = [] } = await apiRequest('/exams');
    select.innerHTML = '<option value="">Select an exam</option>' + data.map(exam =>
      `<option value="${String(exam.exam_id)}">${String(exam.title || `Exam ${exam.exam_id}`).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}</option>`
    ).join('');
  } catch (error) {
    select.innerHTML = '<option value="">Could not load exams</option>';
    if (typeof showToast === 'function') showToast(error.message, 'danger');
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!select.value) return;
    const submit = form.querySelector('[type="submit"]');
    submit.disabled = true;
    try {
      const { data = {} } = await apiRequest(`/faculty/exams/${encodeURIComponent(select.value)}/results/publish`, { method: 'POST' });
      if (typeof showToast === 'function') showToast(`${data.published_count || 0} results published; students have been notified.`, 'success');
      window.location.href = `/evaluation/results/list.html?exam_id=${encodeURIComponent(select.value)}`;
    } catch (error) {
      submit.disabled = false;
      if (typeof showToast === 'function') showToast(error.message, 'danger');
    }
  });
}
