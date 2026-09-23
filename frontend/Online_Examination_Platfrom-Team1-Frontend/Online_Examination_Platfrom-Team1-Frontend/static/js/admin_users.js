document.addEventListener('DOMContentLoaded', () => {
  loadUsers();
});

async function loadUsers() {
  const tbody = document.getElementById('users-table-body');

  if (!tbody) return;

  tbody.innerHTML = `
    <tr>
      <td colspan="7" class="text-center text-muted py-4">
        Loading users...
      </td>
    </tr>
  `;

  try {
    const response = await apiRequest('/admin/users');

    if (!response?.success || !Array.isArray(response.data)) {
      throw new Error('Invalid users response.');
    }

    renderUsers(response.data);
  } catch (error) {
    console.error('Failed to load users:', error);

    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-danger py-4">
          Failed to load users.
        </td>
      </tr>
    `;
  }
}

function renderUsers(users) {
  const tbody = document.getElementById('users-table-body');

  if (!tbody) return;

  if (users.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-muted py-4">
          No users found.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = users.map(user => {
    const fullName = `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim();

    return `
      <tr>
        <td>#${user.user_id}</td>

        <td class="fw-semibold">
          ${escapeHtml(fullName)}
        </td>

        <td>
          ${escapeHtml(user.email ?? '-')}
        </td>

        <td>
          ${escapeHtml(user.phone ?? '-')}
        </td>

        <td>
          ${renderRoleBadge(user.role)}
        </td>

        <td>
          ${formatDate(user.created_at)}
        </td>

        <td>
          ${renderStatusBadge(user.is_active)}
        </td>

        <td>
          <a
            href="/admin/users/edit.html?user_id=${user.user_id}"
            class="btn btn-sm btn-outline-light me-1"
            title="Edit User"
          >
            <i class="bi bi-pencil"></i>
          </a>

          <button
            type="button"
            class="btn btn-sm btn-outline-info"
            title="${user.is_active ? 'Deactivate User' : 'Activate User'}"
            onclick="toggleUserStatus(${user.user_id}, ${user.is_active})"
          >
            <i class="bi ${user.is_active ? 'bi-person-dash' : 'bi-person-check'}"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderRoleBadge(role) {
  const normalizedRole = String(role ?? '').toUpperCase();

  let badgeClass = 'bg-secondary';

  if (normalizedRole === 'ADMIN') {
    badgeClass = 'bg-danger';
  } else if (normalizedRole === 'FACULTY') {
    badgeClass = 'bg-info';
  } else if (normalizedRole === 'STUDENT') {
    badgeClass = 'bg-success';
  }

  return `
    <span class="badge ${badgeClass}">
      ${escapeHtml(normalizedRole || '-')}
    </span>
  `;
}

function renderStatusBadge(isActive) {
  return isActive
    ? '<span class="status-badge badge-active">Active</span>'
    : '<span class="badge bg-secondary">Inactive</span>';
}

async function toggleUserStatus(userId, currentStatus) {
  const action = currentStatus ? 'deactivate' : 'activate';

  const confirmed = window.confirm(
    `Are you sure you want to ${action} user #${userId}?`
  );

  if (!confirmed) return;

  try {
    const response = await apiRequest(`/admin/users/${userId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({
        is_active: !currentStatus
      })
    });

    if (!response?.success) {
      throw new Error(response?.message || 'Failed to update user status.');
    }

    showToast(
      response.message || 'User status updated successfully.',
      'success'
    );

    await loadUsers();
  } catch (error) {
    console.error('Failed to update user status:', error);

    showToast(
      error.message || 'Failed to update user status.',
      'error'
    );
  }
}

function formatDate(value) {
  if (!value) return '-';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}