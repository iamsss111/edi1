/* API-backed Student, Faculty, and notification views. */

function lifecycleEscape(value) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);
}

function lifecycleDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function lifecycleError(error) {
  const message = error?.message || 'Unable to load this page.';
  if (typeof showToast === 'function') showToast(message, 'danger');
  else console.error(message);
}

async function lifecycleRequest(path, options) {
  if (typeof apiRequest !== 'function') throw new Error('API client is unavailable.');
  return apiRequest(path, options);
}

async function loadStudentSubjects() {
  const container = document.getElementById('studentSubjectCards');
  if (!container) return;
  try {
    const { data = [] } = await lifecycleRequest('/student/subjects');
    if (!data.length) {
      container.innerHTML = '<div class="col-12"><div class="glass-card p-4 text-muted">There are no active subject offerings for your department and semester yet.</div></div>';
      return;
    }
    container.innerHTML = data.map(subject => `<div class="col-md-6 col-xl-4"><article class="glass-card p-4 h-100 d-flex flex-column">
      <div class="d-flex justify-content-between gap-2"><span class="badge bg-primary-subtle text-primary">${lifecycleEscape(subject.subject_code)}</span><span class="badge ${subject.is_enrolled ? 'bg-success' : 'bg-secondary'}">${subject.is_enrolled ? 'Enrolled' : 'Available'}</span></div>
      <h2 class="h5 fw-bold mt-3 mb-1">${lifecycleEscape(subject.subject_name)}</h2>
      <p class="text-muted small">${lifecycleEscape(subject.description || 'No description provided.')}</p>
      <div class="border rounded p-3 section-bg small mb-3"><div><i class="bi bi-person-badge me-2"></i><strong>${lifecycleEscape(subject.faculty?.name)}</strong></div><div class="text-muted mt-1">${lifecycleEscape(subject.faculty?.designation || 'Faculty')} · Semester ${lifecycleEscape(subject.semester)} · Academic year ${lifecycleEscape(subject.academic_year)}</div>${subject.credits ? `<div class="text-muted mt-1">${lifecycleEscape(subject.credits)} credits</div>` : ''}</div>
      <div class="mt-auto">${subject.is_enrolled ? '<a class="btn btn-outline-primary w-100" href="/student/exams/available.html">View subject exams</a>' : `<button class="btn btn-primary-custom w-100 js-enroll-subject" data-offering-id="${lifecycleEscape(subject.faculty_subject_id)}">Enroll in subject</button>`}</div>
    </article></div>`).join('');
    if (container.dataset.enrollBound !== 'true') {
      container.dataset.enrollBound = 'true';
      container.addEventListener('click', async event => {
        const button = event.target.closest('.js-enroll-subject');
        if (!button) return;
        button.disabled = true;
        try {
          await lifecycleRequest(`/student/subjects/${encodeURIComponent(button.dataset.offeringId)}/enroll`, { method: 'POST' });
          if (typeof showToast === 'function') showToast('You are enrolled in this subject.', 'success');
          await loadStudentSubjects();
        } catch (error) {
          button.disabled = false;
          lifecycleError(error);
        }
      });
    }
  } catch (error) {
    container.innerHTML = '<div class="col-12 text-danger">Could not load subject offerings.</div>';
    lifecycleError(error);
  }
}

async function loadAvailableExams() {
  const container = document.getElementById('availableExamCards');
  if (!container) return;
  container.innerHTML = '<div class="col-12 text-muted">Loading available exams…</div>';
  try {
    const { data = [] } = await lifecycleRequest('/student/exams/available');
    if (!data.length) {
      container.innerHTML = '<div class="col-12"><div class="glass-card p-4 text-muted">No published exams are currently scheduled for your department.</div></div>';
      return;
    }
    container.innerHTML = data.map(exam => {
      const registered = exam.registration_status === 'Registered';
      const inProgress = new Date(exam.schedule?.start_time) <= new Date();
      const registrationOpen = exam.registration_open === true;
      return `<div class="col-md-6 col-lg-4">
        <div class="glass-card p-4 h-100 d-flex flex-column justify-content-between">
          <div>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="status-badge ${registered ? 'badge-active' : 'badge-scheduled'}">${registered ? (inProgress ? 'IN PROGRESS' : 'REGISTERED') : (registrationOpen ? 'REGISTRATION OPEN' : 'REGISTRATION CLOSED')}</span>
              <span class="font-monospace text-muted small">${lifecycleEscape(exam.subject?.subject_code)}</span>
            </div>
            <h5 class="fw-bold mb-2">${lifecycleEscape(exam.title)}</h5>
            <p class="text-muted small mb-3">${lifecycleEscape(exam.subject?.name)}</p>
            <div class="p-3 rounded border section-bg small mb-3">
              <div class="d-flex justify-content-between mb-1"><span>Duration</span><span>${lifecycleEscape(exam.duration_minutes)} minutes</span></div>
              <div class="d-flex justify-content-between mb-1"><span>Total marks</span><span>${lifecycleEscape(exam.total_marks)}</span></div>
              <div class="d-flex justify-content-between"><span>Starts</span><strong class="text-info">${lifecycleEscape(lifecycleDate(exam.schedule?.start_time))}</strong></div>
            </div>
          </div>
          ${registered
            ? `<a class="btn btn-success w-100" href="/exam_runtime/lobby.html?exam_id=${encodeURIComponent(exam.exam_id)}">Enter Exam Lobby</a>`
            : (registrationOpen ? `<button class="btn btn-primary-custom w-100 js-register-exam" data-exam-id="${lifecycleEscape(exam.exam_id)}">Register</button>` : '<button class="btn btn-secondary w-100" disabled>Registration closed</button>')}
        </div>
      </div>`;
    }).join('');
    if (container.dataset.registerHandlerAttached !== 'true') {
      container.dataset.registerHandlerAttached = 'true';
      container.addEventListener('click', async event => {
      const button = event.target.closest('.js-register-exam');
      if (!button) return;
      button.disabled = true;
      try {
        await lifecycleRequest(`/student/exams/${encodeURIComponent(button.dataset.examId)}/register`, { method: 'POST' });
        if (typeof showToast === 'function') showToast('You are registered for the exam.', 'success');
        await loadAvailableExams();
      } catch (error) {
        button.disabled = false;
        lifecycleError(error);
      }
      });
    }
  } catch (error) {
    container.innerHTML = '<div class="col-12 text-danger">Could not load available exams.</div>';
    lifecycleError(error);
  }
}

async function loadRegisteredExams() {
  const body = document.getElementById('registeredExamsBody');
  if (!body) return;
  body.innerHTML = '<tr><td colspan="6" class="text-muted">Loading registrations…</td></tr>';
  try {
    const { data = [] } = await lifecycleRequest('/student/registrations');
    if (!data.length) {
      body.innerHTML = '<tr><td colspan="6" class="text-muted">You have no exam registrations yet.</td></tr>';
      return;
    }
    body.innerHTML = data.map(registration => {
      const exam = registration.exam || {};
      const action = registration.status === 'Registered'
        ? `<a class="btn btn-sm btn-success" href="/exam_runtime/lobby.html?exam_id=${encodeURIComponent(registration.exam_id)}">Open lobby</a>`
        : '<span class="text-muted">No action</span>';
      return `<tr>
        <td>${lifecycleEscape(registration.registration_id)}</td>
        <td><strong>${lifecycleEscape(exam.title)}</strong><br><small class="text-muted">${lifecycleEscape(exam.subject?.subject_code)}</small></td>
        <td>${lifecycleEscape(lifecycleDate(registration.registered_at))}</td>
        <td><span class="badge bg-success">ELIGIBLE</span></td>
        <td>${lifecycleEscape(registration.status)}</td>
        <td>${action}</td>
      </tr>`;
    }).join('');
  } catch (error) {
    body.innerHTML = '<tr><td colspan="6" class="text-danger">Could not load registrations.</td></tr>';
    lifecycleError(error);
  }
}

async function loadStudentResults() {
  const body = document.getElementById('studentResultsBody');
  if (!body) return;
  body.innerHTML = '<tr><td colspan="7" class="text-muted">Loading results…</td></tr>';
  try {
    const { data = [] } = await lifecycleRequest('/student/results');
    if (!data.length) {
      body.innerHTML = '<tr><td colspan="7" class="text-muted">No results have been published yet.</td></tr>';
      return;
    }
    body.innerHTML = data.map(result => `<tr>
      <td>${lifecycleEscape(result.result_id)}</td>
      <td><strong>${lifecycleEscape(result.exam_title)}</strong><br><small class="text-muted">${lifecycleEscape(result.subject_code)}</small></td>
      <td>${lifecycleEscape(result.percentage)}%</td>
      <td><span class="badge bg-primary">${lifecycleEscape(result.grade || '—')}</span></td>
      <td><span class="badge ${result.result_status === 'Pass' ? 'bg-success' : 'bg-danger'}">${lifecycleEscape(result.result_status)}</span></td>
      <td>${lifecycleEscape(lifecycleDate(result.published_at))}</td>
      <td><a class="btn btn-sm btn-outline-info" href="/student/results/detail.html?result_id=${encodeURIComponent(result.result_id)}">View scorecard</a></td>
    </tr>`).join('');
  } catch (error) {
    body.innerHTML = '<tr><td colspan="7" class="text-danger">Could not load results.</td></tr>';
    lifecycleError(error);
  }
}

async function loadStudentResultDetail() {
  const breakdown = document.getElementById('resultQuestionBreakdown');
  if (!breakdown) return;
  const resultId = new URLSearchParams(location.search).get('result_id');
  if (!resultId) {
    breakdown.innerHTML = '<div class="alert alert-warning">Choose a result from your results list first.</div>';
    return;
  }
  try {
    const { data } = await lifecycleRequest(`/student/results/${encodeURIComponent(resultId)}`);
    document.getElementById('resultExamLabel').textContent = `${data.exam?.subject_code || ''} • ${data.exam?.title || ''}`;
    document.getElementById('resultTotalMarks').textContent = data.total_marks;
    document.getElementById('resultObtainedMarks').textContent = data.obtained_marks;
    document.getElementById('resultPercentage').textContent = `${data.percentage}%`;
    document.getElementById('resultGrade').textContent = `${data.grade || '—'} (${String(data.result_status || '').toUpperCase()})`;
    const rows = data.question_breakdown || [];
    breakdown.innerHTML = rows.length ? rows.map(question => {
      const options = question.correct_options || [];
      return `<div class="p-3 rounded border section-bg mb-3">
        <div class="d-flex justify-content-between mb-2"><span class="badge bg-secondary">Q${lifecycleEscape(question.question_order)}</span><strong>${lifecycleEscape(question.marks_obtained)} / ${lifecycleEscape(question.marks_available)} marks</strong></div>
        <p class="fw-medium mb-2">${lifecycleEscape(question.question_text)}</p>
        <div class="small text-muted">Your answer: <strong>${lifecycleEscape(question.selected_option?.option_text || question.answer_text || 'Not answered')}</strong></div>
        ${options.length ? `<div class="small text-muted">Correct answer: <strong>${options.map(o => lifecycleEscape(o.option_text)).join(', ')}</strong></div>` : ''}
        <div class="small text-info mt-2">${lifecycleEscape(question.remarks)}</div>
      </div>`;
    }).join('') : '<p class="text-muted">No question breakdown is available.</p>';
  } catch (error) {
    breakdown.innerHTML = '<div class="alert alert-danger">Could not load this published result.</div>';
    lifecycleError(error);
  }
}

async function loadFacultyDashboard() {
  if (!document.querySelector('[data-faculty-stat]')) return;
  try {
    const { data = {} } = await lifecycleRequest('/faculty/dashboard/statistics');
    document.querySelectorAll('[data-faculty-stat]').forEach(node => {
      node.textContent = data[node.dataset.facultyStat] ?? 0;
    });
    await loadFacultyPending(document.getElementById('facultyDashboardPendingBody'));
  } catch (error) { lifecycleError(error); }
}

async function loadFacultyPending(target = document.getElementById('facultyPendingEvaluationsBody')) {
  if (!target) return;
  target.innerHTML = '<tr><td colspan="7" class="text-muted">Loading evaluation queue…</td></tr>';
  try {
    const { data = [] } = await lifecycleRequest('/faculty/evaluations/pending');
    if (!data.length) {
      target.innerHTML = '<tr><td colspan="7" class="text-muted">No submitted attempts need evaluation or publication.</td></tr>';
      return;
    }
    target.innerHTML = data.map(attempt => {
      const name = attempt.student?.name || 'Student';
      const action = `<a class="btn btn-sm btn-outline-success" href="/evaluation/evaluate.html?attempt_id=${encodeURIComponent(attempt.attempt_id)}">Review attempt</a>`;
      return `<tr>
        <td>${lifecycleEscape(attempt.attempt_id)}</td><td>${lifecycleEscape(name)}</td>
        <td>${lifecycleEscape(attempt.exam_title || `Exam ${attempt.exam_id || ''}`)}</td>
        <td>${lifecycleEscape(lifecycleDate(attempt.submitted_at))}</td>
        <td>${attempt.score == null ? '—' : lifecycleEscape(attempt.score)}</td>
        <td><span class="badge ${attempt.evaluation_status === 'PENDING' ? 'bg-warning text-dark' : 'bg-info'}">${lifecycleEscape(attempt.evaluation_status || 'PENDING')}</span></td>
        <td>${action}</td>
      </tr>`;
    }).join('');
  } catch (error) {
    target.innerHTML = '<tr><td colspan="7" class="text-danger">Could not load the faculty queue.</td></tr>';
    lifecycleError(error);
  }
}

async function loadNotifications() {
  const button = document.getElementById('notifDropdown');
  const center = document.getElementById('notificationCenterList');
  if (!button && !center) return;
  try {
    const [notificationResponse, countResponse] = await Promise.all([
      lifecycleRequest('/notifications'),
      lifecycleRequest('/notifications/unread-count'),
    ]);
    const notifications = notificationResponse.data || [];
    const count = countResponse.data?.unread_count || 0;
    const badge = button?.closest('.dropdown')?.querySelector('.badge.bg-primary');
    if (badge) badge.textContent = `${count} unread`;
    const dot = button?.querySelector('.badge-dot');
    if (dot) dot.classList.toggle('d-none', count === 0);
    const menuList = button?.closest('.dropdown')?.querySelector('.list-group');
    if (menuList) {
      menuList.innerHTML = notifications.slice(0, 5).map(n => `<a href="/notifications/center.html" class="list-group-item list-group-item-action p-3 ${n.is_read ? '' : 'fw-semibold'}"><strong>${lifecycleEscape(n.title)}</strong><small class="d-block text-muted">${lifecycleEscape(lifecycleDate(n.created_at))}</small><span>${lifecycleEscape(n.message)}</span></a>`).join('') || '<div class="p-3 text-muted">No notifications.</div>';
    }
    if (center) {
      center.innerHTML = notifications.map(n => `<div class="list-group-item bg-transparent text-white p-3 ${n.is_read ? '' : 'border-start border-info border-3'}">
        <div class="d-flex justify-content-between mb-1"><span class="badge bg-info">${lifecycleEscape(n.notification_type)}</span><small class="text-muted">${lifecycleEscape(lifecycleDate(n.created_at))}</small></div>
        <h6 class="fw-bold mb-1 text-white">${lifecycleEscape(n.title)}</h6><p class="text-muted small mb-2">${lifecycleEscape(n.message)}</p>
        ${n.is_read ? '<span class="small text-muted">Read</span>' : `<button class="btn btn-sm btn-outline-secondary js-mark-notification-read" data-notification-id="${lifecycleEscape(n.notification_id)}">Mark as read</button>`}
      </div>`).join('') || '<div class="p-3 text-muted">No notifications yet.</div>';
    }
  } catch (error) { lifecycleError(error); }
}

function initializeLifecycleUI() {
  loadStudentSubjects();
  loadAvailableExams();
  loadRegisteredExams();
  loadStudentResults();
  loadStudentResultDetail();
  loadFacultyDashboard();
  loadFacultyPending();
  loadNotifications();

  if (document.getElementById('availableExamCards')) {
    let lastRefresh = Date.now();
    window.addEventListener('focus', () => {
      if (Date.now() - lastRefresh > 5000) {
        lastRefresh = Date.now();
        loadAvailableExams();
      }
    });
    window.setInterval(() => {
      if (!document.hidden) {
        lastRefresh = Date.now();
        loadAvailableExams();
      }
    }, 30000);
  }

  document.getElementById('markAllNotificationsRead')?.addEventListener('click', async () => {
    try {
      await lifecycleRequest('/notifications/read-all', { method: 'PATCH' });
      await loadNotifications();
      if (typeof showToast === 'function') showToast('Notifications marked as read.', 'success');
    } catch (error) { lifecycleError(error); }
  });
  document.getElementById('notificationCenterList')?.addEventListener('click', async event => {
    const button = event.target.closest('.js-mark-notification-read');
    if (!button) return;
    try {
      await lifecycleRequest(`/notifications/${encodeURIComponent(button.dataset.notificationId)}/read`, { method: 'PATCH' });
      await loadNotifications();
    } catch (error) { lifecycleError(error); }
  });
}

document.addEventListener('DOMContentLoaded', initializeLifecycleUI);
