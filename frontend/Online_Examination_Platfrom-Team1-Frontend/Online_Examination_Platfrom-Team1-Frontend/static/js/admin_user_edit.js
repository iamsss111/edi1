document.addEventListener('DOMContentLoaded', () => {
    initializeEditUserPage();
});

async function initializeEditUserPage() {
    const userId = getUserIdFromUrl();

    if (!userId) {
        showToast('User ID is missing from the URL.', 'error');
        return;
    }

    try {
        const response = await apiRequest(`/admin/users/${userId}`);

        if (!response?.success || !response.data) {
            throw new Error(response?.message || 'Failed to load user.');
        }

        populateUserForm(response.data);
    } catch (error) {
        console.error('Failed to load user:', error);
        showToast(error.message || 'Failed to load user.', 'error');
    }

    const editForm = document.getElementById('edit-user-form');
    if (editForm) {
        editForm.addEventListener('submit', updateUser);
    }

    const roleForm = document.getElementById('change-role-form');
    if (roleForm) {
        roleForm.addEventListener('submit', changeUserRole);
    }
    const resetPasswordForm = document.getElementById('reset-password-form');

if (resetPasswordForm) {
    resetPasswordForm.addEventListener('submit', resetUserPassword);
}
}
async function resetUserPassword(event) {
    event.preventDefault();

    const userId = getUserIdFromUrl();
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const submitButton = document.getElementById('reset-password-button');

    if (!userId) {
        showToast('User ID is missing from the URL.', 'error');
        return;
    }

    if (!newPassword) {
        showToast('New password is required.', 'error');
        return;
    }

    if (newPassword.length < 8) {
        showToast('Password must be at least 8 characters long.', 'error');
        return;
    }

    if (newPassword !== confirmPassword) {
        showToast('Passwords do not match.', 'error');
        return;
    }

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Resetting...';
    }

    try {
        const response = await apiRequest(
            `/admin/users/${userId}/password`,
            {
                method: 'PATCH',
                body: JSON.stringify({
                    new_password: newPassword
                })
            }
        );

        if (!response?.success) {
            throw new Error(
                response?.message || 'Failed to reset password.'
            );
        }

        showToast(
            response.message || 'Password reset successfully.',
            'success'
        );

        document.getElementById('newPassword').value = '';
        document.getElementById('confirmPassword').value = '';

    } catch (error) {
        console.error('Failed to reset password:', error);

        showToast(
            error.message || 'Failed to reset password.',
            'error'
        );
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Reset Password';
        }
    }
}

function getUserIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('user_id');
}

function populateUserForm(user) {
    document.getElementById('firstName').value = user.first_name ?? '';
    document.getElementById('lastName').value = user.last_name ?? '';
    document.getElementById('email').value = user.email ?? '';
    document.getElementById('phone').value = user.phone ?? '';

    document.getElementById('userIdDisplay').textContent = `#${user.user_id}`;
    document.getElementById('currentRoleDisplay').innerHTML = renderRoleBadge(user.role);
    document.getElementById('currentStatusDisplay').innerHTML = renderStatusBadge(user.is_active);
    document.getElementById('createdAtDisplay').textContent = formatDateTime(user.created_at);

    const roleSelect = document.getElementById('role');
    if (roleSelect) {
        roleSelect.value = user.role ?? '';
    }

    document.getElementById('page-title').textContent =
        `Edit User #${user.user_id}`;

    document.getElementById('user-subtitle').textContent =
        `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim();

    document.title = `Edit User #${user.user_id} - MMCOE Admin Portal`;
}

async function updateUser(event) {
    event.preventDefault();

    const userId = getUserIdFromUrl();

    if (!userId) {
        showToast('User ID is missing from the URL.', 'error');
        return;
    }

    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();

    if (!firstName || !lastName || !email) {
        showToast('First name, last name, and email are required.', 'error');
        return;
    }

    const submitButton = document.getElementById('update-user-button');

    if (submitButton) {
        submitButton.disabled = true;
    }

    try {
        const response = await apiRequest(`/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email,
                phone: phone || null
            })
        });

        if (!response?.success) {
            throw new Error(response?.message || 'Failed to update user.');
        }

        showToast(
            response.message || 'User updated successfully.',
            'success'
        );

        setTimeout(() => {
            window.location.href = '/admin/users/list.html';
        }, 800);

    } catch (error) {
        console.error('Failed to update user:', error);
        showToast(error.message || 'Failed to update user.', 'error');
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
        }
    }
}

async function changeUserRole(event) {
    event.preventDefault();

    const userId = getUserIdFromUrl();
    const roleForm = event.currentTarget;
    const roleSelect = roleForm.querySelector('#role');
    const submitButton = roleForm.querySelector('#change-role-button');

    if (!userId) {
        showToast('User ID is missing from the URL.', 'error');
        return;
    }

    if (!roleSelect) {
        showToast('Role selector was not found.', 'error');
        return;
    }

    const selectedRole = roleSelect.value;

    if (!selectedRole) {
        showToast('Please select a role.', 'error');
        return;
    }

    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Saving...';
    }

    try {
        // Send exactly the value selected in this role form.
        const response = await apiRequest(`/admin/users/${userId}/role`, {
            method: 'PATCH',
            body: JSON.stringify({
                role: selectedRole
            })
        });

        if (!response?.success || !response.data) {
            throw new Error(
                response?.message || 'Failed to change user role.'
            );
        }

        /*
         * Re-read the user from the backend.
         * This makes the UI reflect the actual persisted database value
         * instead of assuming that the PATCH succeeded.
         */
        const refreshedUser = await apiRequest(`/admin/users/${userId}`);

        if (!refreshedUser?.success || !refreshedUser.data) {
            throw new Error('Role was updated, but the updated user could not be loaded.');
        }

        populateUserForm(refreshedUser.data);

        showToast(
            'User role updated successfully.',
            'success'
        );

    } catch (error) {
        console.error('Failed to change user role:', error);

        showToast(
            error.message || 'Failed to change user role.',
            'error'
        );
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.textContent = 'Save Role';
        }
    }
}

function renderRoleBadge(role) {
    const roleClasses = {
        ADMIN: 'bg-danger',
        FACULTY: 'bg-primary',
        STUDENT: 'bg-success'
    };

    const roleLabels = {
        ADMIN: 'Admin',
        FACULTY: 'Faculty',
        STUDENT: 'Student'
    };

    const normalizedRole = role ?? '';
    const badgeClass = roleClasses[normalizedRole] || 'bg-secondary';
    const label = roleLabels[normalizedRole] || normalizedRole || 'Unknown';

    return `<span class="badge ${badgeClass}">${escapeHtml(label)}</span>`;
}

function renderStatusBadge(isActive) {
    return isActive
        ? '<span class="badge bg-success">Active</span>'
        : '<span class="badge bg-secondary">Inactive</span>';
}

function formatDateTime(value) {
    if (!value) {
        return '-';
    }

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