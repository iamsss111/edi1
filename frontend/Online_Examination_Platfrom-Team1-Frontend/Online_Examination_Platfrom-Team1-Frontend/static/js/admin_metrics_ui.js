document.addEventListener('DOMContentLoaded', loadAdminMetricsPage);

async function loadAdminMetricsPage() {
  const bodies = [...document.querySelectorAll('main table tbody')];
  if (!bodies.length) return;
  try {
    const [statsResponse, dbResponse, auditResponse] = await Promise.all([
      apiRequest('/admin/dashboard/statistics'), apiRequest('/db-health'), apiRequest('/admin/audit-logs')
    ]);
    const stats = statsResponse.data || {}, metrics = [
      ['DATABASE_CONNECTION', dbResponse.success ? 'Connected' : 'Unavailable', 'status'],
      ['USERS_ACTIVE', stats.users?.active, 'users'], ['USERS_TOTAL', stats.users?.total, 'users'],
      ['EXAMS_TOTAL', stats.exams?.total, 'exams'], ['QUESTIONS_ACTIVE', stats.questions?.active, 'questions'],
      ['ATTEMPTS_TOTAL', stats.attempts?.total, 'attempts'], ['RESULTS_PENDING', stats.results?.pending, 'results']
    ];
    bodies[0].innerHTML = metrics.map(([name, value, unit]) => `<tr><td class="fw-semibold">${metricsEscape(name)}</td><td class="font-monospace">${metricsEscape(value ?? '—')}</td><td>${metricsEscape(unit)}</td><td class="text-muted">${new Date().toLocaleString()}</td></tr>`).join('');
    if (bodies[1]) bodies[1].innerHTML = '<tr><td colspan="4" class="text-muted">Feature-flag records and controls are not implemented by this backend.</td></tr>';
    if (bodies[2]) bodies[2].innerHTML = '<tr><td colspan="3" class="text-muted">Persistent system configuration is not implemented by this backend.</td></tr>';
    const logs = auditResponse.data || [];
    if (bodies[3]) bodies[3].innerHTML = logs.length ? logs.slice(0, 20).map(row => `<tr><td class="fw-semibold">${metricsEscape(row.action)}</td><td><span class="badge bg-info">RECORDED</span></td><td>${metricsEscape(row.entity_type || 'Platform')}</td><td>${metricsEscape(row.created_at || '—')}</td></tr>`).join('') : '<tr><td colspan="4" class="text-muted">No audit events have been recorded.</td></tr>';
  } catch (error) { showToast(error.message || 'Could not load system metrics.', 'danger'); }
}

function metricsEscape(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
