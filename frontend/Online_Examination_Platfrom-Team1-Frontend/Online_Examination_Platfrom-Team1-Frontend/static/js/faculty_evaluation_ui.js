document.addEventListener('DOMContentLoaded', loadFacultyAttemptReview);

function evaluationEscape(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

async function loadFacultyAttemptReview() {
  const panel = document.getElementById('attemptEvaluationPanel');
  if (!panel) return;
  const attemptId = new URLSearchParams(location.search).get('attempt_id');
  if (!attemptId) {
    panel.innerHTML = '<div class="col-12 alert alert-warning">Open this page from a pending attempt.</div>';
    return;
  }
  panel.innerHTML = '<div class="col-12 text-muted">Loading student submission…</div>';
  try {
    const { data } = await apiRequest(`/faculty/attempts/${encodeURIComponent(attemptId)}`);
    document.getElementById('evaluationAttemptSummary').textContent = `${data.student?.name || 'Student'} • Attempt ${data.attempt_number} • ${data.exam_title}`;
    const answers = data.answers || [];
    panel.innerHTML = `<div class="col-lg-8">
      ${answers.map(answer => `<article class="glass-card p-4 mb-3">
        <div class="d-flex justify-content-between mb-2"><span class="badge bg-primary">Question ${evaluationEscape(answer.question_order)}</span><span>${answer.marks_obtained == null ? 'Not evaluated' : `${evaluationEscape(answer.marks_obtained)} / ${evaluationEscape(answer.marks_available)} marks`}</span></div>
        <p class="fw-semibold">${evaluationEscape(answer.question_text)}</p>
        <p class="small text-muted mb-1">Student answer: <strong>${evaluationEscape(answer.selected_option?.option_text || answer.answer_text || 'Not answered')}</strong></p>
        <p class="small text-muted mb-0">Correct answer: <strong>${(answer.correct_options || []).map(o => evaluationEscape(o.option_text)).join(', ') || '—'}</strong></p>
      </article>`).join('') || '<div class="glass-card p-4">No answer records are available.</div>'}
    </div>
    <div class="col-lg-4"><div class="glass-card p-4 position-sticky" style="top:90px">
      <h5 class="fw-bold">Attempt summary</h5>
      <p class="text-muted">Status: ${evaluationEscape(data.status)}</p>
      <p>Score: <strong>${data.score == null ? 'Not evaluated' : `${evaluationEscape(data.score)} / ${evaluationEscape(data.answers?.reduce((sum, a) => sum + Number(a.marks_available || 0), 0))}`}</strong></p>
      <p class="small text-muted">Objective questions are auto-graded. This workflow does not support manual marking of descriptive answers.</p>
      ${data.score == null
        ? '<button id="evaluateAttemptButton" class="btn btn-primary w-100">Evaluate objective answers</button>'
        : data.result_published
          ? '<span class="badge bg-success">Result published</span>'
          : `<button id="publishAttemptResultButton" data-result-id="${evaluationEscape(data.result_id)}" class="btn btn-success w-100">Publish result</button>`}
      <a class="btn btn-link w-100 mt-2" href="/evaluation/pending.html">Back to queue</a>
    </div></div>`;
    document.getElementById('evaluateAttemptButton')?.addEventListener('click', async event => {
      const button = event.currentTarget;
      button.disabled = true;
      try {
        await apiRequest(`/faculty/attempts/${encodeURIComponent(attemptId)}/evaluate`, { method: 'POST' });
        if (typeof showToast === 'function') showToast('Objective answers evaluated.', 'success');
        await loadFacultyAttemptReview();
      } catch (error) { button.disabled = false; if (typeof showToast === 'function') showToast(error.message, 'danger'); }
    });
    document.getElementById('publishAttemptResultButton')?.addEventListener('click', async event => {
      const button = event.currentTarget;
      button.disabled = true;
      try {
        await apiRequest(`/faculty/results/${encodeURIComponent(button.dataset.resultId)}/publish`, { method: 'POST' });
        if (typeof showToast === 'function') showToast('Result published and the student notified.', 'success');
        await loadFacultyAttemptReview();
      } catch (error) { button.disabled = false; if (typeof showToast === 'function') showToast(error.message, 'danger'); }
    });
  } catch (error) {
    panel.innerHTML = '<div class="col-12 alert alert-danger">Could not load this attempt.</div>';
    if (typeof showToast === 'function') showToast(error.message, 'danger');
  }
}
