document.addEventListener('DOMContentLoaded', () => {
    loadSubjects();
});

async function loadSubjects() {
    const tbody = document.getElementById('subject-table-body');

    if (!tbody) return;

    tbody.innerHTML = `
        <tr>
            <td colspan="8" class="text-center text-muted py-4">
                Loading subjects...
            </td>
        </tr>
    `;

    try {
        const response = await apiRequest('/admin/subjects', {
            method: 'GET'
        });

        const subjects = response.data || [];

        if (subjects.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted py-4">
                        No subjects found.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = subjects.map(subject => `
            <tr>
                <td>#${subject.subject_id}</td>

                <td>
                    <span class="font-monospace text-info">
                        ${escapeHtml(subject.subject_code)}
                    </span>
                </td>

                <td class="fw-semibold">
                    ${escapeHtml(subject.subject_name)}
                </td>

                <td class="text-muted">
                    ${escapeHtml(subject.description || '—')}
                </td>

                <td>
                    <span class="badge bg-secondary">
                        ${subject.credits}
                    </span>
                </td>

                <td class="text-muted">
                    ${subject.department_id ?? '—'}
                </td>

                <td>
                    ${
                        subject.is_active
                            ? '<span class="status-badge badge-active">Active</span>'
                            : '<span class="status-badge badge-inactive">Inactive</span>'
                    }
                </td>

                <td>
                    <div class="d-flex gap-1">
                        <a
                            href="/subjects/edit.html?id=${subject.subject_id}"
                            class="btn btn-sm btn-outline-light"
                            title="Edit Subject"
                        >
                            <i class="bi bi-pencil"></i>
                        </a>

                        <button
                            type="button"
                            class="btn btn-sm btn-outline-light"
                            title="${subject.is_active ? 'Deactivate' : 'Activate'} Subject"
                            onclick="toggleSubjectStatus(${subject.subject_id}, ${subject.is_active})"
                        >
                            <i class="bi ${subject.is_active ? 'bi-toggle-on' : 'bi-toggle-off'}"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Failed to load subjects:', error);

        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger py-4">
                    Failed to load subjects.
                </td>
            </tr>
        `;
    }
}

async function toggleSubjectStatus(subjectId, currentStatus) {
    const action = currentStatus ? 'deactivate' : 'activate';

    if (!confirm(`Are you sure you want to ${action} this subject?`)) {
        return;
    }

    try {
        await apiRequest(`/admin/subjects/${subjectId}/status`, {
            method: 'PATCH',
            body: JSON.stringify({
                is_active: !currentStatus
            })
        });

        showToast(
            `Subject ${action}d successfully.`,
            'success'
        );

        await loadSubjects();

    } catch (error) {
        console.error('Failed to update subject status:', error);

        showToast(
            error.message || 'Failed to update subject status.',
            'danger'
        );
    }
}

function escapeHtml(value) {
    const div = document.createElement('div');
    div.textContent = value ?? '';
    return div.innerHTML;
}