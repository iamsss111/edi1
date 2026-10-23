document.addEventListener('DOMContentLoaded', async () => {
  const form = document.getElementById('editExamForm'); if (!form) return;
  const id = new URLSearchParams(location.search).get('exam_id');
  if (!id) { showToast('Exam id is missing.', 'danger'); return; }
  try {
    const { data } = await apiRequest(`/exams/${encodeURIComponent(id)}`);
    document.getElementById('editExamCode').value = `EXAM-${data.exam_id}`;
    document.getElementById('editExamTitle').value = data.title || '';
    document.getElementById('editExamTotalMarks').value = data.total_marks ?? '';
    document.getElementById('editExamPassMarks').value = data.pass_marks ?? '';
    document.getElementById('editExamDuration').value = data.duration_minutes ?? '';
    const subject = document.getElementById('editExamSubject'); if (subject) subject.value = `Subject #${data.subject_id}`;
  } catch (error) { showToast(error.message, 'danger'); }
  form.addEventListener('submit', async event => {
    event.preventDefault(); const button = form.querySelector('[type="submit"]'); button.disabled = true;
    try {
      await apiRequest(`/exams/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify({
        title: document.getElementById('editExamTitle').value.trim(),
        total_marks: Number(document.getElementById('editExamTotalMarks').value),
        pass_marks: Number(document.getElementById('editExamPassMarks').value),
        duration_minutes: Number(document.getElementById('editExamDuration').value)
      }) });
      showToast('Exam updated.', 'success'); window.location.href = `/exams/detail.html?exam_id=${encodeURIComponent(id)}`;
    } catch (error) { button.disabled = false; showToast(error.message, 'danger'); }
  });
});
