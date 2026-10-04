let adminStudents = [];
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('student-search')?.addEventListener('input', (event) => renderAdminStudents(event.target.value));
  loadAdminStudents();
});
async function loadAdminStudents() {
  const body = document.getElementById('student-table-body');
  try { const response = await apiRequest('/admin/students', { method: 'GET' }); adminStudents = response.data || []; renderAdminStudents(); }
  catch (error) { body.innerHTML = `<tr><td colspan="10" class="text-center text-danger py-4">${escapeHtml(error.message || 'Failed to load students.')}</td></tr>`; }
}
function renderAdminStudents(search = '') {
  const term = search.toLowerCase().trim(); const rows = adminStudents.filter((student) => !term || JSON.stringify(student).toLowerCase().includes(term)); const body = document.getElementById('student-table-body');
  if (!rows.length) { body.innerHTML = '<tr><td colspan="10" class="text-center text-muted py-4">No students found.</td></tr>'; return; }
  body.innerHTML = rows.map((student) => `<tr><td>${student.student_id}</td><td>${escapeHtml(`${student.first_name || ''} ${student.last_name || ''}`)}</td><td>${escapeHtml(student.email)}</td><td>${escapeHtml(student.department_name)}</td><td>${escapeHtml(student.roll_number)}</td><td>${escapeHtml(student.enrollment_number)}</td><td>${escapeHtml(student.year)}</td><td>${escapeHtml(student.semester)}</td><td>${student.is_active ? 'Active' : 'Inactive'}</td><td><a class="btn btn-sm btn-outline-light" href="/admin/students/edit.html?id=${student.student_id}">Edit</a> <button class="btn btn-sm btn-outline-light" onclick="toggleStudentStatus(${student.student_id}, ${student.is_active})">${student.is_active ? 'Deactivate' : 'Activate'}</button></td></tr>`).join('');
}
async function toggleStudentStatus(studentId, isActive) { try { await apiRequest(`/admin/students/${studentId}/status`, { method: 'PATCH', body: JSON.stringify({ is_active: !isActive }) }); await loadAdminStudents(); } catch (error) { showToast(error.message || 'Failed to update student status.', 'danger'); } }
function escapeHtml(value) { const div = document.createElement('div'); div.textContent = value ?? ''; return div.innerHTML; }