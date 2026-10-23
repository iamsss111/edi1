document.addEventListener('DOMContentLoaded', loadStudentDashboardData);

async function loadStudentDashboardData() {
  const upcoming = document.getElementById('studentUpcomingContainer');
  if (!upcoming) return;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  try {
    const [availableResponse, registrationsResponse, resultsResponse] = await Promise.all([
      apiRequest('/student/exams/available'), apiRequest('/student/registrations'), apiRequest('/student/results')
    ]);
    const available = availableResponse.data || [];
    const registrations = registrationsResponse.data || [];
    const results = resultsResponse.data || [];
    document.getElementById('studentStatSubjects').textContent = new Set(registrations.map(r => r.exam?.subject?.subject_id).filter(Boolean)).size;
    document.getElementById('studentStatCompleted').textContent = results.length;
    document.getElementById('studentStatUpcoming').textContent = available.length;
    const average = results.length ? results.reduce((sum, r) => sum + Number(r.percentage || 0), 0) / results.length : null;
    document.getElementById('studentStatAverage').textContent = average == null ? '—' : `${average.toFixed(1)}%`;
    upcoming.innerHTML = available.length ? available.slice(0, 3).map(exam => {
      const registered = exam.registration_status === 'Registered';
      return `<div class="p-3 rounded border section-bg mb-3 d-flex align-items-center justify-content-between"><div><div class="d-flex align-items-center gap-2 mb-1"><span class="badge ${registered ? 'bg-success' : 'bg-info'}">${registered ? 'REGISTERED' : 'REGISTRATION OPEN'}</span><span class="font-monospace text-muted small">${escape(exam.subject?.subject_code)}</span></div><h6 class="fw-bold m-0 text-dark">${escape(exam.title)}</h6><small class="text-muted">${escape(exam.duration_minutes)} min • ${escape(exam.total_marks)} marks • Starts ${escape(new Date(exam.schedule?.start_time).toLocaleString())}</small></div>${registered ? `<a href="/exam_runtime/lobby.html?exam_id=${encodeURIComponent(exam.exam_id)}" class="btn btn-sm btn-success">Enter lobby</a>` : '<a href="/student/exams/available.html" class="btn btn-sm btn-outline-info">Register</a>'}</div>`;
    }).join('') : '<div class="text-muted p-3">No upcoming exams are available.</div>';
    const body = document.getElementById('studentRecentResultsBody');
    if (body) body.innerHTML = results.slice(0, 5).map(result => `<tr><td>${escape(result.exam_title)}</td><td>${escape(result.percentage)}%</td><td>${escape(result.grade || '—')}</td><td>${escape(result.result_status)}</td><td><a class="btn btn-sm btn-outline-info" href="/student/results/detail.html?result_id=${encodeURIComponent(result.result_id)}">View</a></td></tr>`).join('') || '<tr><td colspan="5" class="text-muted">No results have been published.</td></tr>';
  } catch (error) { showToast(error.message || 'Could not load dashboard data.', 'danger'); }
}
