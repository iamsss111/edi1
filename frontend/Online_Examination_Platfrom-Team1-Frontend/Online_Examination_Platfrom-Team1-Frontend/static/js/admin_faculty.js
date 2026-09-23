document.addEventListener('DOMContentLoaded', () => {
    loadFaculty();

    const searchInput = document.getElementById('faculty-search');

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            filterFaculty(searchInput.value);
        });
    }
});

let facultyRecords = [];


async function loadFaculty() {
    const tbody = document.getElementById('faculty-table-body');

    if (!tbody) {
        return;
    }

    tbody.innerHTML = `
        <tr>
            <td colspan="9" class="text-center text-muted py-4">
                Loading faculty...
            </td>
        </tr>
    `;

    try {
        const response = await apiRequest('/admin/faculty', {
            method: 'GET'
        });

        facultyRecords = response.data || [];

        renderFaculty(facultyRecords);

    } catch (error) {
        console.error('Failed to load faculty:', error);

        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-danger py-4">
                    Failed to load faculty.
                </td>
            </tr>
        `;
    }
}


function renderFaculty(records) {
    const tbody = document.getElementById('faculty-table-body');

    if (!tbody) {
        return;
    }

    if (records.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    No faculty records found.
                </td>
            </tr>
        `;

        return;
    }

    tbody.innerHTML = records.map(faculty => {

        const fullName =
            `${faculty.first_name || ''} ${faculty.last_name || ''}`.trim();

        const status = faculty.is_active
            ? `
                <span class="status-badge badge-active">
                    Active
                </span>
              `
            : `
                <span class="status-badge badge-inactive">
                    Inactive
                </span>
              `;

        return `
            <tr>

                <td>
                    #${faculty.faculty_id}
                </td>

                <td>
                    <span class="font-monospace text-info">
                        ${escapeHtml(faculty.employee_number || '—')}
                    </span>
                </td>

                <td class="fw-semibold">
                    ${escapeHtml(fullName || '—')}
                </td>

                <td>
                    ${escapeHtml(faculty.email || '—')}
                </td>

                <td>
                    ${escapeHtml(faculty.phone || '—')}
                </td>

                <td>
                    ${escapeHtml(faculty.designation || '—')}
                </td>

                <td>
                    ${escapeHtml(faculty.department_name || '—')}
                </td>

                <td>
                    ${status}
                </td>

                <td>

                    <div class="d-flex gap-1">

                        <a
                            href="/admin/faculty/edit.html?id=${faculty.faculty_id}"
                            class="btn btn-sm btn-outline-light"
                            title="Edit Faculty"
                        >
                            <i class="bi bi-pencil"></i>
                        </a>

                        <button
                            type="button"
                            class="btn btn-sm btn-outline-light"
                            title="${faculty.is_active ? 'Deactivate' : 'Activate'} Faculty"
                            onclick="toggleFacultyStatus(${faculty.faculty_id}, ${faculty.is_active})"
                        >
                            <i class="bi ${
                                faculty.is_active
                                    ? 'bi-toggle-on'
                                    : 'bi-toggle-off'
                            }"></i>
                        </button>

                    </div>

                </td>

            </tr>
        `;

    }).join('');
}


function filterFaculty(searchTerm) {

    const term =
        searchTerm.trim().toLowerCase();

    if (!term) {
        renderFaculty(facultyRecords);
        return;
    }

    const filtered =
        facultyRecords.filter(faculty => {

            const searchableText = [
                faculty.employee_number,
                faculty.first_name,
                faculty.last_name,
                faculty.email,
                faculty.phone,
                faculty.designation,
                faculty.department_name
            ]
                .filter(Boolean)
                .join(' ')
                .toLowerCase();

            return searchableText.includes(term);

        });

    renderFaculty(filtered);
}


async function toggleFacultyStatus(
    facultyId,
    currentStatus
) {

    const action =
        currentStatus
            ? 'deactivate'
            : 'activate';

    if (
        !confirm(
            `Are you sure you want to ${action} this faculty member?`
        )
    ) {
        return;
    }

    try {

        await apiRequest(
            `/admin/faculty/${facultyId}/status`,
            {
                method: 'PATCH',

                body: JSON.stringify({
                    is_active: !currentStatus
                })
            }
        );

        showToast(
            `Faculty ${action}d successfully.`,
            'success'
        );

        await loadFaculty();

    } catch (error) {

        console.error(
            'Failed to update faculty status:',
            error
        );

        showToast(
            error.message ||
            'Failed to update faculty status.',
            'danger'
        );

    }
}


function escapeHtml(value) {

    const div =
        document.createElement('div');

    div.textContent =
        value ?? '';

    return div.innerHTML;
}