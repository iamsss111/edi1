document.addEventListener('DOMContentLoaded', () => {
  const manualButton = document.getElementById('manualQuestionModeButton');
  const csvButton = document.getElementById('csvQuestionModeButton');
  const manualSection = document.getElementById('manualQuestionSection');
  const csvSection = document.getElementById('csvQuestionSection');
  if (!manualButton || !csvButton || !manualSection || !csvSection) return;

  const showMode = mode => {
    const csvMode = mode === 'csv';
    manualSection.classList.toggle('d-none', csvMode);
    csvSection.classList.toggle('d-none', !csvMode);
    manualButton.classList.toggle('btn-primary-custom', !csvMode);
    manualButton.classList.toggle('btn-outline-primary', csvMode);
    csvButton.classList.toggle('btn-primary-custom', csvMode);
    csvButton.classList.toggle('btn-outline-primary', !csvMode);
  };
  manualButton.addEventListener('click', () => showMode('manual'));
  csvButton.addEventListener('click', () => showMode('csv'));

  const form = document.getElementById('questionCsvUploadForm');
  form?.addEventListener('submit', async event => {
    event.preventDefault();
    const button = document.getElementById('questionCsvUploadButton');
    const status = document.getElementById('questionCsvUploadStatus');
    const fileInput = document.getElementById('questionCsvFile');
    const file = fileInput?.files?.[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv')) {
      status.className = 'small mb-3 text-danger';
      status.textContent = 'Choose a .csv file.';
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      status.className = 'small mb-3 text-danger';
      status.textContent = 'This file exceeds the 5 MB limit.';
      return;
    }

    button.disabled = true;
    status.className = 'small mb-3 text-muted';
    status.textContent = 'Validating and importing questions…';
    try {
      const formData = new FormData(form);
      const result = await apiRequest('/questions/import-csv', { method: 'POST', body: formData });
      status.className = 'small mb-3 text-success';
      status.textContent = result.message || `${result.data?.imported_count || 0} questions imported.`;
      if (typeof showToast === 'function') showToast(status.textContent, 'success');
      window.setTimeout(() => { window.location.href = '/questions/list.html'; }, 700);
    } catch (error) {
      status.className = 'small mb-3 text-danger';
      status.textContent = error.message || 'Question CSV import failed.';
      button.disabled = false;
    }
  });
});
