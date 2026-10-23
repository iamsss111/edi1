document.addEventListener('DOMContentLoaded', initializeExamReport);

async function initializeExamReport() {
  const select = document.getElementById('reportExamSelect'); if (!select) return;
  try {
    const { data = [] } = await apiRequest('/exams');
    select.innerHTML = '<option value="">Select an exam</option>' + data.map(e => `<option value="${e.exam_id}">${reportEscape(e.title)}</option>`).join('');
    const requested = new URLSearchParams(location.search).get('exam_id');
    if (requested) select.value = requested;
    if (!select.value && data.length) select.value = String(data[0].exam_id);
    select.addEventListener('change', () => loadExamReport(select.value));
    if (select.value) await loadExamReport(select.value);
  } catch (error) { select.innerHTML = '<option value="">Could not load exams</option>'; showToast(error.message, 'danger'); }
}

async function loadExamReport(examId) {
  if (!examId) return;
  try {
    const [analyticsResponse, resultsResponse] = await Promise.all([
      apiRequest(`/faculty/exams/${encodeURIComponent(examId)}/analytics`),
      apiRequest(`/exams/${encodeURIComponent(examId)}/results`)
    ]);
    const a = analyticsResponse.data || {}, results = resultsResponse.data?.results || [];
    document.getElementById('reportExamTitle').textContent = `${resultsResponse.data?.exam_title || 'Exam'} · Live analytics`;
    document.getElementById('reportCandidateCount').textContent = a.total_candidates ?? 0;
    const published = results.filter(r => r.published), passes = published.filter(r => r.result_status === 'Pass').length;
    document.getElementById('reportPassRate').textContent = published.length ? `${(passes * 100 / published.length).toFixed(1)}%` : '—';
    const average = published.length ? published.reduce((sum, r) => sum + Number(r.percentage || 0), 0) / published.length : null;
    document.getElementById('reportAverage').textContent = average == null ? '—' : `${average.toFixed(2)}%`;
    document.getElementById('reportSubmitted').textContent = a.submitted ?? 0;
    const gradeCounts = published.reduce((counts, result) => { const grade = result.grade || 'Ungraded'; counts[grade] = (counts[grade] || 0) + 1; return counts; }, {});
    document.getElementById('reportGradeDistribution').innerHTML = Object.entries(gradeCounts).length ? Object.entries(gradeCounts).map(([grade, count]) => {
      const percent = Math.round(count * 100 / published.length);
      return `<div><div class="d-flex justify-content-between small mb-1"><span>${reportEscape(grade)}</span><span>${count} results (${percent}%)</span></div><div class="progress bg-light mb-2" style="height:10px"><div class="progress-bar bg-info" style="width:${percent}%"></div></div></div>`;
    }).join('') : '<p class="text-muted mb-0">No published results yet.</p>';
    const body = document.getElementById('reportAccuracyBody');
    body.innerHTML = a.question_accuracy?.length ? a.question_accuracy.map(q => `<tr><td class="fw-bold">Q${reportEscape(q.question_order)}</td><td>${reportEscape(q.question_type)}</td><td><span class="badge bg-secondary">${reportEscape(q.difficulty)}</span></td><td>${q.accuracy_percentage == null ? '—' : `${reportEscape(q.accuracy_percentage)}%`}</td></tr>`).join('') : '<tr><td colspan="4" class="text-muted">No submitted responses to analyze.</td></tr>';
  } catch (error) { showToast(error.message, 'danger'); }
}

function reportEscape(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
