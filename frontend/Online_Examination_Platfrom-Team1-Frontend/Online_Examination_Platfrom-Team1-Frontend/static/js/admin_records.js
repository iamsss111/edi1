const adminRecordConfig = {
  students: { endpoint: '/admin/students', detail: '/admin/students', id: 'student_id', columns: ['student_id', 'first_name', 'last_name', 'email', 'department_name', 'roll_number', 'enrollment_number', 'year', 'semester', 'is_active'] },
  exams: { endpoint: '/admin/exams', detail: '/admin/exams', id: 'exam_id', columns: ['exam_id', 'title', 'subject.subject_code', 'faculty.email', 'duration_minutes', 'status', 'question_count', 'candidate_count'] },
  questions: { endpoint: '/admin/questions', detail: '/admin/questions', id: 'question_id', columns: ['question_id', 'question_text', 'question_type', 'marks', 'difficulty', 'subject.subject_code', 'option_count', 'is_active'] },
  registrations: { endpoint: '/admin/registrations', detail: '/admin/registrations', id: 'registration_id', columns: ['registration_id', 'exam.title', 'subject.subject_code', 'student.first_name', 'student.last_name', 'student.email', 'status', 'registered_at'] },
  attempts: { endpoint: '/admin/attempts', detail: '/admin/attempts', id: 'attempt_id', columns: ['attempt_id', 'exam.title', 'student.first_name', 'student.last_name', 'attempt_number', 'status', 'score', 'started_at'] },
  results: { endpoint: '/admin/results', detail: '/admin/results', id: 'result_id', columns: ['result_id', 'exam.title', 'student.first_name', 'student.last_name', 'total_marks', 'obtained_marks', 'percentage', 'grade', 'result_status'] }
};

let activeRecordType = 'students';
let activeRecordRows = [];

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-record]').forEach((tab) => tab.addEventListener('click', () => {
    document.querySelectorAll('[data-record]').forEach((item) => item.classList.remove('active'));
    tab.classList.add('active');
    activeRecordType = tab.dataset.record;
    loadAdminRecords();
  }));
  document.getElementById('record-search')?.addEventListener('input', (event) => renderAdminRecords(event.target.value));
  loadAdminRecords();
});

async function loadAdminRecords() {
  const config = adminRecordConfig[activeRecordType];
  const body = document.getElementById('record-body');
  body.innerHTML = '<tr><td colspan="12" class="text-center text-muted py-4">Loading records...</td></tr>';
  try {
    const response = await apiRequest(config.endpoint, { method: 'GET' });
    activeRecordRows = response.data || [];
    renderRecordHead(config.columns);
    renderAdminRecords();
  } catch (error) {
    body.innerHTML = `<tr><td colspan="12" class="text-center text-danger py-4">${escapeHtml(error.message || 'Failed to load records.')}</td></tr>`;
  }
}

function renderRecordHead(columns) {
  document.getElementById('record-head').innerHTML = `<tr>${columns.map((column) => `<th>${escapeHtml(column.replace('.', ' / ').replaceAll('_', ' '))}</th>`).join('')}<th>Actions</th></tr>`;
}

function renderAdminRecords(searchTerm = '') {
  const config = adminRecordConfig[activeRecordType];
  const term = searchTerm.trim().toLowerCase();
  const rows = activeRecordRows.filter((row) => !term || JSON.stringify(row).toLowerCase().includes(term));
  const body = document.getElementById('record-body');
  if (!rows.length) {
    body.innerHTML = `<tr><td colspan="${config.columns.length + 1}" class="text-center text-muted py-4">No ${activeRecordType} found.</td></tr>`;
    return;
  }
  body.innerHTML = rows.map((row) => `<tr>${config.columns.map((column) => `<td>${escapeHtml(formatRecordValue(getNestedValue(row, column)))}</td>`).join('')}<td><button class="btn btn-sm btn-outline-light" onclick="loadRecordDetail('${activeRecordType}', ${Number(row[config.id])})">Details</button> ${activeRecordType === 'attempts' ? `<button class="btn btn-sm btn-outline-info" onclick="loadIntegrityEvents(${Number(row.attempt_id)})">Integrity</button>` : ''}${activeRecordType === 'questions' ? `<button class="btn btn-sm btn-outline-warning" onclick="toggleQuestionStatus(${Number(row.question_id)}, ${Boolean(row.is_active)})">${row.is_active ? 'Deactivate' : 'Activate'}</button>` : ''}</td></tr>`).join('');
}

async function loadRecordDetail(type, id) {
  const panel = document.getElementById('integrity-panel');
  const target = document.getElementById('integrity-body');
  panel.classList.remove('d-none');
  panel.querySelector('h5').textContent = `${type[0].toUpperCase()}${type.slice(1)} details`;
  target.textContent = 'Loading details...';
  try { const response = await apiRequest(`${adminRecordConfig[type].detail}/${id}`, { method: 'GET' }); target.innerHTML = `<pre class="mb-0 small">${escapeHtml(JSON.stringify(response.data, null, 2))}</pre>`; } catch (error) { target.textContent = error.message || 'Failed to load details.'; }
}

async function toggleQuestionStatus(questionId, isActive) {
  try { await apiRequest(`/admin/questions/${questionId}/status`, { method: 'PATCH', body: JSON.stringify({ is_active: !isActive }) }); await loadAdminRecords(); } catch (error) { showToast(error.message || 'Failed to update question status.', 'danger'); }
}

async function loadIntegrityEvents(attemptId) {
  const panel = document.getElementById('integrity-panel');
  const target = document.getElementById('integrity-body');
  panel.classList.remove('d-none');
  target.textContent = 'Loading integrity events...';
  try {
    const response = await apiRequest(`/admin/attempts/${attemptId}/integrity-events`, { method: 'GET' });
    const events = response.data?.events || [];
    target.innerHTML = events.length ? events.map((event) => `<div class="border-bottom py-2"><strong>${escapeHtml(event.action || 'Event')}</strong> <span class="text-muted">${escapeHtml(event.created_at || '')}</span><div>${escapeHtml(event.details || '')}</div></div>`).join('') : 'No integrity events recorded.';
  } catch (error) {
    target.textContent = error.message || 'Failed to load integrity events.';
  }
}

function getNestedValue(record, path) {
  return path.split('.').reduce((value, key) => value == null ? null : value[key], record);
}

function formatRecordValue(value) {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'boolean') return value ? 'Active' : 'Inactive';
  return value;
}

function escapeHtml(value) {
  const div = document.createElement('div');
  div.textContent = value ?? '';
  return div.innerHTML;
}