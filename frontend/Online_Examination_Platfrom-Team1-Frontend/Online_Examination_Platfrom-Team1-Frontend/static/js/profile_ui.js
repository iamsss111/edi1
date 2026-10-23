document.addEventListener('DOMContentLoaded', loadMyProfile);

async function loadMyProfile() {
  const loading = document.getElementById('profileLoading');
  const errorBox = document.getElementById('profileError');
  try {
    const response = await apiRequest('/profile');
    if (!response?.success || !response.data) {
      throw new Error(response?.message || 'Could not load your profile.');
    }
    const user = response.data;
    const role = String(user.role || 'ACCOUNT').toUpperCase();
    const roleNames = { STUDENT: 'Student', FACULTY: 'Faculty', ADMIN: 'Administrator' };
    document.title = `My Profile - ${roleNames[role] || 'Account'}`;
    document.getElementById('profileName').textContent = user.full_name || 'My Profile';
    document.getElementById('profileRole').textContent = roleNames[role] || role;
    document.getElementById('profileRoleBadge').textContent = roleNames[role] || role;
    document.getElementById('profileAvatar').textContent = (user.first_name || '?').charAt(0).toUpperCase();
    document.getElementById('profileBackLink').href = ({
      STUDENT: '/student/dashboard.html',
      FACULTY: '/faculty/dashboard.html',
      ADMIN: '/admin/dashboard.html',
    })[role] || '/';

    const accountFields = [
      ['Account ID', user.user_id],
      ['Email', user.email],
      ['Phone', user.phone],
      ['Account status', user.is_active ? 'Active' : 'Inactive'],
      ['Member since', formatProfileDate(user.created_at)],
    ];
    renderProfileFields('profileDetails', accountFields);

    const profile = user.profile || {};
    const roleFields = {
      STUDENT: [
        ['Student ID', profile.student_id],
        ['Roll number', profile.roll_number],
        ['Enrollment number', profile.enrollment_number],
        ['Department', [profile.department_code, profile.department_name].filter(Boolean).join(' · ')],
        ['Academic year', profile.year],
        ['Semester', profile.semester],
        ['Student status', profile.is_active ? 'Active' : 'Inactive'],
      ],
      FACULTY: [
        ['Faculty ID', profile.faculty_id],
        ['Employee number', profile.employee_number],
        ['Designation', profile.designation],
        ['Department', [profile.department_code, profile.department_name].filter(Boolean).join(' · ')],
      ],
      ADMIN: [['Account type', profile.account_type || 'Administrator']],
    }[role] || [];
    document.getElementById('roleProfileTitle').textContent = `${roleNames[role] || 'Account'} details`;
    renderProfileFields('roleProfileDetails', roleFields);
    document.getElementById('roleProfileSection').classList.toggle('d-none', roleFields.length === 0);
    const completionNotice = document.getElementById('profileCompletionNotice');
    if (role === 'FACULTY' && !profile.faculty_id) {
      completionNotice.textContent = 'This account is assigned the Faculty role, but its Faculty profile is not linked yet. An administrator must add the employee number, designation, and department in Faculty Management.';
      completionNotice.classList.remove('d-none');
    } else {
      completionNotice.classList.add('d-none');
      completionNotice.textContent = '';
    }
    document.getElementById('profileContent').classList.remove('d-none');
  } catch (error) {
    errorBox.textContent = error.message || 'Could not load your profile. Sign in again if your session expired.';
    errorBox.classList.remove('d-none');
  } finally {
    loading.classList.add('d-none');
  }
}

function renderProfileFields(containerId, fields) {
  const container = document.getElementById(containerId);
  container.replaceChildren();
  fields.forEach(([label, value]) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'col-md-6';
    const card = document.createElement('div');
    card.className = 'border rounded p-3 h-100 bg-white';
    const heading = document.createElement('div');
    heading.className = 'small text-muted mb-1';
    heading.textContent = label;
    const content = document.createElement('div');
    content.className = 'fw-semibold text-dark';
    content.textContent = value === null || value === undefined || value === '' ? 'Not provided' : String(value);
    card.append(heading, content);
    wrapper.append(card);
    container.append(wrapper);
  });
}

function formatProfileDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString();
}
