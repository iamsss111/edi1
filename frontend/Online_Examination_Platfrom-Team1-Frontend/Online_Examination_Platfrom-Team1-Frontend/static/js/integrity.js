/*
 * Browser Integrity Monitoring
 *
 * Frontend only:
 * - Detects tab switching
 * - Detects window focus loss
 * - Detects fullscreen exit
 * - Records integrity events in examState
 * - Shows a warning to the student
 *
 * The backend remains authoritative for exam integrity.
 */

const INTEGRITY_EVENT_COOLDOWN = 1500;

let lastIntegrityEventTime = 0;

function createIntegrityEvent(type, metadata = {}) {
  return {
    type,
    occurred_at: new Date().toISOString(),
    metadata
  };
}

function recordIntegrityEvent(type, metadata = {}) {
  if (typeof examState === 'undefined') {
    return;
  }

  const now = Date.now();

  // Avoid duplicate events caused by multiple browser APIs firing
  // for the same user action.
  if (now - lastIntegrityEventTime < INTEGRITY_EVENT_COOLDOWN) {
    return;
  }

  lastIntegrityEventTime = now;

  if (!Array.isArray(examState.integrityEvents)) {
    examState.integrityEvents = [];
  }

  const event = createIntegrityEvent(type, metadata);

  examState.integrityEvents.push(event);

  saveExamState();

  console.warn('Exam integrity event:', event);

  showIntegrityWarning(event);
}

function getIntegrityMessage(type) {
  switch (type) {
    case 'TAB_SWITCH':
      return 'You left the exam tab. Please return to the examination window.';

    case 'WINDOW_BLUR':
      return 'The examination window lost focus. Please return to the exam.';

    case 'FULLSCREEN_EXIT':
      return 'Fullscreen mode was exited. Please return to fullscreen mode if required.';

    default:
      return 'An examination environment change was detected.';
  }
}

function showIntegrityWarning(event) {
  const existingWarning = document.getElementById('integrityWarning');

  if (existingWarning) {
    existingWarning.remove();
  }

  const warning = document.createElement('div');

  warning.id = 'integrityWarning';
  warning.className =
    'alert alert-warning position-fixed top-0 start-50 translate-middle-x mt-3 shadow';
  warning.style.zIndex = '9999';
  warning.style.maxWidth = '90%';

  warning.innerHTML = `
    <strong>Exam Integrity Notice</strong><br>
    ${getIntegrityMessage(event.type)}
  `;

  document.body.appendChild(warning);

  setTimeout(() => {
    warning.remove();
  }, 5000);
}

function initializeIntegrityMonitoring() {
  if (typeof examState === 'undefined') {
    return;
  }

  if (!Array.isArray(examState.integrityEvents)) {
    examState.integrityEvents = [];
    saveExamState();
  }

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      recordIntegrityEvent('TAB_SWITCH');
    }
  });

  window.addEventListener('blur', () => {
    recordIntegrityEvent('WINDOW_BLUR');
  });

  document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
      recordIntegrityEvent('FULLSCREEN_EXIT');
    }
  });
}