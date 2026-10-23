document.addEventListener('DOMContentLoaded', () => {
    initializeSubjectDirectory();
});

async function initializeSubjectDirectory() {
    const mode = document.body.dataset.subjectMode;
    if (mode === 'admin') {
        await loadSubjects();
        return;
    }
    try {
        const { data: user } = await apiRequest('/profile');
        const identityStorage = localStorage.getItem(AUTH_TOKEN_KEY)
            ? localStorage
            : sessionStorage.getItem(AUTH_TOKEN_KEY)
                ? sessionStorage
                : null;
        if (identityStorage && user) identityStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
        if (user?.role === 'FACULTY') await loadFacultySubjects();
        else if (user?.role === 'ADMIN') {
            window.location.replace('/admin/subjects/list.html');
            return;
        }
        else showSubjectDirectoryError('Sign in with a faculty or administrator account to view subjects.');
    } catch (error) {
        showSubjectDirectoryError(error.message || 'Could not verify your account role.');
    }
}

function showSubjectDirectoryError(message) {
    const body = document.getElementById('subject-table-body');
    if (body) body.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">${escapeHtml(message)}</td></tr>`;
}

async function loadFacultySubjects() {
    const tbody = document.getElementById('subject-table-body');
    if (!tbody) return;

    const addButton = document.getElementById('add-subject-btn');
    if (addButton) addButton.classList.add('d-none');
    document.getElementById('subject-page-title').textContent = 'My Academic Subjects';
    document.getElementById('subject-page-description').textContent =
        'Subjects assigned to you by your administrator, with semester and academic year.';
    document.getElementById('subject-table-head').innerHTML = `
        <tr class="text-muted">
            <th>Code</th><th>Subject Name</th><th>Description</th><th>Credits</th>
            <th>Semester</th><th>Academic Year</th><th>Status</th>
        </tr>`;
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">Loading assigned subjects…</td></tr>';

    try {
        const response = await apiRequest('/subjects', { method: 'GET' });
        const assignments = Array.isArray(response.data) ? response.data : [];
        if (!assignments.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No active subjects are assigned to your faculty profile.</td></tr>';
            return;
        }

        tbody.innerHTML = assignments.map(assignment => `
            <tr>
                <td><span class="font-monospace text-info">${escapeHtml(assignment.subject_code)}</span></td>
                <td class="fw-semibold">${escapeHtml(assignment.subject_name)}</td>
                <td class="text-muted">${escapeHtml(assignment.description || '—')}</td>
                <td><span class="badge bg-secondary">${escapeHtml(assignment.credits)}</span></td>
                <td>${escapeHtml(assignment.semester)}</td>
                <td>${escapeHtml(assignment.year)}</td>
                <td><span class="status-badge badge-active">Assigned</span></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load faculty subjects:', error);
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">${escapeHtml(error.message || 'Failed to load assigned subjects.')}</td></tr>`;
    }
}

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

        const adminMode = document.body.dataset.subjectMode === 'admin';
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
                        ${adminMode ? '' : `<a href="/subjects/edit.html?id=${subject.subject_id}" class="btn btn-sm btn-outline-light" title="Edit Subject"><i class="bi bi-pencil"></i></a>`}

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
