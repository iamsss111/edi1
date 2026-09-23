document.addEventListener('DOMContentLoaded', () => {
  loadAuditLogs();
});

async function loadAuditLogs() {
  const tbody = document.getElementById('audit-log-body');

  if (!tbody) return;

  tbody.innerHTML = `
    <tr>
      <td colspan="8" class="text-center text-muted py-4">
        Loading audit logs...
      </td>
    </tr>
  `;

  try {
    const response = await apiRequest('/admin/audit-logs');

    if (!response?.success || !Array.isArray(response.data)) {
      throw new Error('Invalid audit log response.');
    }

    renderAuditLogs(response.data);
  } catch (error) {
    console.error('Failed to load audit logs:', error);

    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-danger py-4">
          Failed to load audit logs.
        </td>
      </tr>
    `;
  }
}

function renderAuditLogs(logs) {
  const tbody = document.getElementById('audit-log-body');

  if (!tbody) return;

  if (logs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-muted py-4">
          No audit logs found.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = logs.map(log => {
    const userName = log.user
      ? `${log.user.first_name ?? ''} ${log.user.last_name ?? ''}`.trim()
      : 'System';

    return `
      <tr>
        <td>
          <span class="font-monospace">#${log.audit_id}</span>
        </td>

        <td class="text-muted">
          ${escapeHtml(formatDateTime(log.created_at))}
        </td>

        <td class="fw-semibold">
          #${log.user?.user_id ?? '-'}
          (${escapeHtml(userName)})
        </td>

        <td>
          <span class="badge bg-secondary">
            ${escapeHtml(log.entity_type ?? '-')}
          </span>
        </td>

        <td>
          <span class="badge bg-primary">
            ${escapeHtml(log.action ?? '-')}
          </span>
        </td>

        <td class="font-monospace text-info">
          ${escapeHtml(log.ip_address ?? '-')}
        </td>

        <td>
          <button
            type="button"
            class="btn btn-sm btn-outline-info"
            onclick="viewAuditLog(${log.audit_id})"
          >
            <i class="bi bi-eye"></i> View
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

async function viewAuditLog(auditId) {
  try {
    const response = await apiRequest(`/admin/audit-logs/${auditId}`);

    if (!response?.success || !response.data) {
      throw new Error('Invalid audit log detail response.');
    }

    showAuditLogDetails(response.data);
  } catch (error) {
    console.error('Failed to load audit log details:', error);
    showToast(
      error.message || 'Failed to load audit log details.',
      'error'
    );
  }
}

function showAuditLogDetails(log) {
  const userName = log.user
    ? `${log.user.first_name ?? ''} ${log.user.last_name ?? ''}`.trim()
    : 'System';

  const details = escapeHtml(
    typeof log.details === 'string'
      ? log.details
      : JSON.stringify(log.details ?? {}, null, 2)
  );

  const existingModal = document.getElementById('auditDetailModal');

  if (existingModal) {
    existingModal.remove();
  }

  const modalHtml = `
    <div
      class="modal fade"
      id="auditDetailModal"
      tabindex="-1"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-shield-check me-2"></i>
              Audit Log #${log.audit_id}
            </h5>

            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>

          <div class="modal-body">

            <div class="row g-3">

              <div class="col-md-6">
                <strong>Audit ID</strong>
                <div class="text-muted">#${log.audit_id}</div>
              </div>

              <div class="col-md-6">
                <strong>Timestamp</strong>
                <div class="text-muted">
                  ${escapeHtml(formatDateTime(log.created_at))}
                </div>
              </div>

              <div class="col-md-6">
                <strong>User</strong>
                <div class="text-muted">
                  #${log.user?.user_id ?? '-'}
                  (${escapeHtml(userName)})
                </div>
              </div>

              <div class="col-md-6">
                <strong>Email</strong>
                <div class="text-muted">
                  ${escapeHtml(log.user?.email ?? '-')}
                </div>
              </div>

              <div class="col-md-6">
                <strong>Entity</strong>
                <div class="text-muted">
                  ${escapeHtml(log.entity_type ?? '-')}
                </div>
              </div>

              <div class="col-md-6">
                <strong>Entity ID</strong>
                <div class="text-muted">
                  ${escapeHtml(log.entity_id ?? '-')}
                </div>
              </div>

              <div class="col-md-6">
                <strong>Action</strong>
                <div>
                  <span class="badge bg-primary">
                    ${escapeHtml(log.action ?? '-')}
                  </span>
                </div>
              </div>

              <div class="col-md-6">
                <strong>IP Address</strong>
                <div class="font-monospace text-info">
                  ${escapeHtml(log.ip_address ?? '-')}
                </div>
              </div>

              <div class="col-12">
                <strong>Details</strong>
                <pre class="bg-light border rounded p-3 mt-2 mb-0">${details}</pre>
              </div>

            </div>

          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              Close
            </button>
          </div>

        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', modalHtml);

  const modalElement = document.getElementById('auditDetailModal');
  const modal = new bootstrap.Modal(modalElement);

  modalElement.addEventListener('hidden.bs.modal', () => {
    modalElement.remove();
  });

  modal.show();
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