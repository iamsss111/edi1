/* API bindings for faculty question workflows and administrator student records. */
const portalEscape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

document.addEventListener('DOMContentLoaded', () => {
  loadQuestionSubjects();
  loadFacultyQuestions();
  bindQuestionCreation();
  bindQuestionEditing();
  loadAdminStudents();
  bindAdminStudentForm();
  bindAdminFacultyForm();
  bindAdminFacultyAssignments();
});

async function loadAdminStudents() {
  const body = document.getElementById('adminStudentsBody');
  if (!body) return;
  try {
    const { data = [] } = await apiRequest('/admin/students');
    body.innerHTML = data.length ? data.map(s => `<tr><td>${portalEscape(s.student_id)}</td><td>${portalEscape(`${s.first_name} ${s.last_name}`)}</td><td>${portalEscape(s.email)}</td><td>${portalEscape(s.roll_number)}</td><td>${portalEscape(s.department_name)}</td><td>${portalEscape(s.year || '—')} / ${portalEscape(s.semester || '—')}</td><td>${s.is_active ? 'Active' : 'Inactive'}</td><td><a class="btn btn-sm btn-outline-primary" href="/admin/students/form.html?id=${encodeURIComponent(s.student_id)}">Edit</a> <button class="btn btn-sm btn-outline-secondary" data-student-status="${s.student_id}" data-active="${s.is_active}">${s.is_active ? 'Deactivate' : 'Activate'}</button></td></tr>`).join('') : '<tr><td colspan="8">No students found.</td></tr>';
    if (!body.dataset.statusBound) {
      body.dataset.statusBound = 'true';
      body.addEventListener('click', async event => {
        const button = event.target.closest('[data-student-status]'); if (!button) return;
        try { await apiRequest(`/admin/students/${button.dataset.studentStatus}/status`, { method: 'PATCH', body: JSON.stringify({ is_active: button.dataset.active !== 'true' }) }); await loadAdminStudents(); }
        catch (error) { showToast(error.message, 'danger'); }
      });
    }
  } catch (error) { body.innerHTML = `<tr><td colspan="8" class="text-danger">${portalEscape(error.message)}</td></tr>`; }
}

function readPortalForm(form, includePassword = false) {
  const payload = Object.fromEntries(new FormData(form).entries());
  for (const key of ['department_id', 'year', 'semester', 'subject_id', 'subject_semester', 'subject_year']) if (payload[key] === '') payload[key] = null; else if (payload[key] != null) payload[key] = Number(payload[key]);
  if (!includePassword) delete payload.password;
  return payload;
}

async function bindAdminStudentForm() {
  const form = document.getElementById('adminStudentForm'); if (!form) return;
  const id = new URLSearchParams(location.search).get('id');
  if (id) {
    document.getElementById('studentFormTitle').textContent = 'Edit student';
    document.getElementById('studentPasswordField').classList.add('d-none');
    form.elements.password.required = false;
    try { const { data } = await apiRequest(`/admin/students/${encodeURIComponent(id)}`); for (const [key, value] of Object.entries(data)) if (form.elements[key]) form.elements[key].value = value ?? ''; }
    catch (error) { showToast(error.message, 'danger'); }
  }
  form.addEventListener('submit', async event => { event.preventDefault(); const button = form.querySelector('[type="submit"]'); button.disabled = true; try { await apiRequest(id ? `/admin/students/${id}` : '/admin/students', { method: id ? 'PUT' : 'POST', body: JSON.stringify(readPortalForm(form, !id)) }); window.location.href = '/admin/students/list.html'; } catch (error) { button.disabled = false; showToast(error.message, 'danger'); } });
}

async function bindAdminFacultyForm() {
  const form = document.getElementById('adminFacultyForm'); if (!form) return;
  const id = new URLSearchParams(location.search).get('id');
  const subjectSelect = form.elements.subject_id;
  const subjectSemester = form.elements.subject_semester;
  const subjectYear = form.elements.subject_year;
  if (subjectSelect && !id) {
    try {
      const { data = [] } = await apiRequest('/admin/subjects');
      subjectSelect.innerHTML = '<option value="">No subject assignment</option>' + data.filter(subject => subject.is_active).map(subject => `<option value="${portalEscape(subject.subject_id)}" data-department="${portalEscape(subject.department_id)}">${portalEscape(subject.subject_code)} — ${portalEscape(subject.subject_name)}</option>`).join('');
      const refreshSubjectOptions = () => {
        const department = String(form.elements.department_id.value || '');
        for (const option of subjectSelect.options) {
          if (!option.value) continue;
          option.hidden = Boolean(department && option.dataset.department !== department);
          option.disabled = option.hidden;
        }
        if (subjectSelect.selectedOptions[0]?.disabled) subjectSelect.value = '';
      };
      form.elements.department_id.addEventListener('input', refreshSubjectOptions);
      form.elements.department_id.addEventListener('change', refreshSubjectOptions);
      refreshSubjectOptions();
    } catch (error) {
      subjectSelect.innerHTML = '<option value="">Could not load subjects</option>';
      showToast(error.message, 'danger');
    }
    const updateAssignmentRequired = () => {
      const selected = Boolean(subjectSelect.value);
      subjectSemester.disabled = subjectYear.disabled = !selected;
      subjectSemester.required = subjectYear.required = selected;
      if (!selected) subjectSemester.value = subjectYear.value = '';
    };
    subjectSelect.addEventListener('change', updateAssignmentRequired);
    updateAssignmentRequired();
  }
  if (id) {
    try { const { data } = await apiRequest(`/admin/faculty/${encodeURIComponent(id)}`); for (const [key, value] of Object.entries(data)) if (form.elements[key]) form.elements[key].value = value ?? ''; }
    catch (error) { showToast(error.message, 'danger'); }
  }
  form.addEventListener('submit', async event => { event.preventDefault(); const button = form.querySelector('[type="submit"]'); button.disabled = true; try { await apiRequest(id ? `/admin/faculty/${id}` : '/admin/faculty', { method: id ? 'PUT' : 'POST', body: JSON.stringify(readPortalForm(form, !id)) }); window.location.href = '/admin/faculty/list.html'; } catch (error) { button.disabled = false; showToast(error.message, 'danger'); } });
}

async function bindAdminFacultyAssignments() {
  const form = document.getElementById('facultySubjectAssignmentForm');
  if (!form) return;
  const facultyId = new URLSearchParams(location.search).get('id');
  if (!facultyId) return;
  const select = form.elements.subject_id;
  const body = document.getElementById('facultyAssignmentsBody');
  try {
    const [{ data: faculty }, { data: subjects = [] }] = await Promise.all([
      apiRequest(`/admin/faculty/${encodeURIComponent(facultyId)}`),
      apiRequest('/admin/subjects'),
    ]);
    const available = subjects.filter(subject => subject.is_active && Number(subject.department_id) === Number(faculty.department_id));
    select.innerHTML = '<option value="">Select a subject</option>' + available.map(subject => `<option value="${portalEscape(subject.subject_id)}">${portalEscape(subject.subject_code)} — ${portalEscape(subject.subject_name)}</option>`).join('');
    if (!available.length) select.innerHTML = '<option value="">No active subjects in this department</option>';
    const year = form.elements.year;
    if (!year.value) year.value = String(new Date().getFullYear());
  } catch (error) {
    select.innerHTML = '<option value="">Could not load department subjects</option>';
    showToast(error.message, 'danger');
  }

  const loadAssignments = async () => {
    body.innerHTML = '<tr><td colspan="5" class="text-muted">Loading assignments…</td></tr>';
    try {
      const { data = [] } = await apiRequest(`/admin/faculty/${encodeURIComponent(facultyId)}/subjects`);
      body.innerHTML = data.length ? data.map(assignment => `<tr>
        <td><strong>${portalEscape(assignment.subject_code)}</strong> — ${portalEscape(assignment.subject_name)}</td>
        <td>${portalEscape(assignment.semester)}</td><td>${portalEscape(assignment.year)}</td>
        <td><span class="badge ${assignment.is_active ? 'bg-success' : 'bg-secondary'}">${assignment.is_active ? 'Active' : 'Inactive'}</span></td>
        <td>${assignment.is_active ? `<button class="btn btn-sm btn-outline-danger js-deactivate-faculty-assignment" data-assignment-id="${portalEscape(assignment.faculty_subject_id)}">Remove</button>` : ''}</td>
      </tr>`).join('') : '<tr><td colspan="5" class="text-muted">No subjects assigned yet.</td></tr>';
    } catch (error) {
      body.innerHTML = `<tr><td colspan="5" class="text-danger">${portalEscape(error.message)}</td></tr>`;
    }
  };

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('[type="submit"]');
    button.disabled = true;
    try {
      await apiRequest(`/admin/faculty/${encodeURIComponent(facultyId)}/subjects`, {
        method: 'POST',
        body: JSON.stringify({
          subject_id: Number(form.elements.subject_id.value),
          semester: Number(form.elements.semester.value),
          year: Number(form.elements.year.value),
        }),
      });
      showToast('Subject assigned to faculty.', 'success');
      form.elements.subject_id.value = '';
      form.elements.semester.value = '';
      await loadAssignments();
    } catch (error) {
      showToast(error.message, 'danger');
    } finally {
      button.disabled = false;
    }
  });

  body.addEventListener('click', async event => {
    const button = event.target.closest('.js-deactivate-faculty-assignment');
    if (!button) return;
    button.disabled = true;
    try {
      await apiRequest(`/admin/faculty-subjects/${encodeURIComponent(button.dataset.assignmentId)}/deactivate`, { method: 'PATCH' });
      showToast('Faculty subject assignment removed.', 'success');
      await loadAssignments();
    } catch (error) {
      button.disabled = false;
      showToast(error.message, 'danger');
    }
  });
  await loadAssignments();
}

async function loadQuestionSubjects() {
  const select = document.getElementById('questionSubjectId');
  if (!select) return;
  try {
    const { data = [] } = await apiRequest('/subjects');
    select.innerHTML = '<option value="">Select a subject</option>' + data.map(s => `<option value="${s.subject_id}">${portalEscape(s.subject_code)} — ${portalEscape(s.subject_name)}</option>`).join('');
  } catch (error) { select.innerHTML = '<option value="">Could not load assigned subjects</option>'; showToast(error.message, 'danger'); }
}

async function loadFacultyQuestions() {
  const body = document.getElementById('facultyQuestionTableBody');
  if (!body) return;
  body.innerHTML = '<tr><td colspan="7">Loading questions…</td></tr>';
  try {
    const { data = [] } = await apiRequest('/questions');
    body.innerHTML = data.length ? data.map(q => `<tr><td>#${portalEscape(q.question_id)}</td><td class="fw-semibold">${portalEscape(q.question_text)}</td><td><span class="badge bg-primary">${portalEscape(q.question_type)}</span></td><td>Subject #${portalEscape(q.subject_id)}</td><td>${portalEscape(q.difficulty)}</td><td>${portalEscape(q.marks)}</td><td><a class="btn btn-sm btn-outline-info" href="/questions/edit.html?id=${encodeURIComponent(q.question_id)}">Edit</a></td></tr>`).join('') : '<tr><td colspan="7">No questions found.</td></tr>';
  } catch (error) { body.innerHTML = `<tr><td colspan="7" class="text-danger">${portalEscape(error.message)}</td></tr>`; }
}

async function bindQuestionEditing() {
  const form = document.getElementById('facultyQuestionEditForm'); if (!form) return;
  const id = new URLSearchParams(location.search).get('id');
  if (!id) { showToast('Question id is missing.', 'danger'); return; }
  try {
    const { data } = await apiRequest(`/questions/${encodeURIComponent(id)}`);
    form.elements.question_text.value = data.question_text || '';
    form.elements.marks.value = data.marks ?? '';
  } catch (error) { showToast(error.message, 'danger'); }
  form.addEventListener('submit', async event => {
    event.preventDefault(); const button = form.querySelector('[type="submit"]'); button.disabled = true;
    try { await apiRequest(`/questions/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify({ question_text: form.elements.question_text.value.trim(), marks: Number(form.elements.marks.value) }) }); window.location.href = '/questions/list.html'; }
    catch (error) { button.disabled = false; showToast(error.message, 'danger'); }
  });
}

function bindQuestionCreation() {
  const form = document.getElementById('facultyQuestionForm');
  if (!form) return;
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('[type="submit"]');
    button.disabled = true;
    const options = [...document.querySelectorAll('#optionsContainer .option-row')].map((row, index) => ({
      option_text: row.querySelector('input[type="text"]').value.trim(), option_order: index + 1,
      is_correct: row.querySelector('input[type="checkbox"]').checked
    })).filter(option => option.option_text);
    try {
      const type = document.getElementById('qTypeSelect').value;
      if (['MCQ', 'TrueFalse'].includes(type) && (!options.length || options.filter(option => option.is_correct).length !== 1)) {
        throw new Error('Add options and mark exactly one correct answer.');
      }
      const response = await apiRequest('/questions', { method: 'POST', body: JSON.stringify({
        subject_id: Number(document.getElementById('questionSubjectId').value),
        question_text: form.querySelector('textarea[required]').value.trim(),
        question_type: type,
        marks: Number(form.querySelector('input[type="number"]').value),
        difficulty: document.getElementById('questionDifficulty').value,
        explanation: [...form.querySelectorAll('textarea')].at(-1).value.trim() || null
      }) });
      if (['MCQ', 'TrueFalse'].includes(type)) {
        for (const option of options) await apiRequest(`/questions/${response.data.question_id}/options`, { method: 'POST', body: JSON.stringify(option) });
      }
      showToast('Question saved.', 'success'); window.location.href = '/questions/list.html';
    } catch (error) { button.disabled = false; showToast(error.message, 'danger'); }
  });
}
