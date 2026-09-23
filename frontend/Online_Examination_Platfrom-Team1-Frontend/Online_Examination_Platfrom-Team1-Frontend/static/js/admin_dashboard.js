document.addEventListener('DOMContentLoaded', () => {
  loadDashboardStatistics();
  loadAuditLogs();
});

async function loadDashboardStatistics() {
  try {
    const response = await apiRequest('/admin/dashboard/statistics');

    if (!response?.success || !response.data) {
      throw new Error('Invalid dashboard statistics response.');
    }

    const stats = response.data;

    setText('total-users', stats.users?.total ?? 0);
    setText('total-roles', 3);
    setText('total-exams', stats.exams?.total ?? 0);
    setText('total-questions', stats.questions?.total ?? 0);

  } catch (error) {
    console.error('Failed to load dashboard statistics:', error);
  }
}

async function loadAuditLogs() {
  try {
    const response = await apiRequest('/admin/audit-logs');

    if (!response?.success || !Array.isArray(response.data)) {
      throw new Error('Invalid audit log response.');
    }

    renderAuditLogs(response.data);
  } catch (error) {
    console.error('Failed to load audit logs:', error);
  }
}

function renderAuditLogs(logs) {
  const tbody = document.getElementById('audit-log-body');

  if (!tbody) return;

  if (logs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="text-center text-muted py-4">
          No audit logs found.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = logs.slice(0, 10).map(log => {
    const userName = log.user
      ? `${log.user.first_name ?? ''} ${log.user.last_name ?? ''}`.trim()
      : 'System';

    return `
      <tr>
        <td class="text-muted">
          ${formatDateTime(log.created_at)}
        </td>
        <td class="fw-semibold">
          ${escapeHtml(userName)}
        </td>
        <td>
          ${escapeHtml(log.entity_type ?? '-')}
        </td>
        <td>
          <span class="badge bg-primary">
            ${escapeHtml(log.action ?? '-')}
          </span>
        </td>
        <td>
          <span class="text-emerald fw-bold">
            RECORDED
          </span>
        </td>
      </tr>
    `;
  }).join('');
}

function setText(id, value) {
  const element = document.getElementById(id);

  if (element) {
    element.textContent = value;
  }
}

function formatDateTime(value) {
  if (!value) return '-';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}