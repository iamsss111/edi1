/*
 * Browser Integrity Monitoring
 *
 * Frontend responsibilities:
 * - Detect tab switching
 * - Detect window focus loss
 * - Detect fullscreen exit
 * - Report integrity events to the backend
 * - Show a warning to the student
 *
 * The backend remains authoritative for exam integrity.
 */

const INTEGRITY_EVENT_COOLDOWN = 1500;
let lastIntegrityEventTime = 0;


/* --------------------------------------------------------------------------
   EVENT CREATION
   -------------------------------------------------------------------------- */

function createIntegrityEvent(type, metadata = {}) {
  return {
    type,
    occurred_at: new Date().toISOString(),
    metadata
  };
}


/* --------------------------------------------------------------------------
   BACKEND REPORTING
   -------------------------------------------------------------------------- */

async function sendIntegrityEvent(event) {
  if (
    typeof examState === 'undefined' ||
    !examState.attemptId
  ) {
    console.warn(
      'Integrity event could not be sent: no active exam attempt.'
    );
    return;
  }

  try {
    const response = await apiRequest(
      `/attempts/${examState.attemptId}/integrity-events`,
      {
        method: 'POST',
        body: JSON.stringify({
  event_type: event.type,
  details: event.metadata
})
      }
    );

    console.log('Integrity event recorded:', response);
  } catch (error) {
    console.error(
      'Failed to record integrity event:',
      error
    );
  }
}


/* --------------------------------------------------------------------------
   EVENT RECORDING
   -------------------------------------------------------------------------- */

function recordIntegrityEvent(type, metadata = {}) {
  if (typeof examState === 'undefined') {
    return;
  }

  const now = Date.now();

  // Prevent duplicate events caused by multiple browser APIs
  // firing for the same user action.
  if (
    now - lastIntegrityEventTime <
    INTEGRITY_EVENT_COOLDOWN
  ) {
    return;
  }

  lastIntegrityEventTime = now;

  const event = createIntegrityEvent(
    type,
    metadata
  );

  console.warn(
    'Exam integrity event:',
    event
  );

  // Send the event to the backend.
  sendIntegrityEvent(event);

  // Show a warning to the student.
  showIntegrityWarning(event);
}


/* --------------------------------------------------------------------------
   WARNING MESSAGE
   -------------------------------------------------------------------------- */

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
  const existingWarning =
    document.getElementById('integrityWarning');

  if (existingWarning) {
    existingWarning.remove();
  }

  const warning =
    document.createElement('div');

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


/* --------------------------------------------------------------------------
   MONITORING INITIALIZATION
   -------------------------------------------------------------------------- */

function initializeIntegrityMonitoring() {
  if (typeof examState === 'undefined') {
    return;
  }

  /*
   * Tab switching / leaving the browser tab.
   */
  document.addEventListener(
    'visibilitychange',
    () => {
      if (
        document.visibilityState === 'hidden'
      ) {
        recordIntegrityEvent(
          'TAB_SWITCH'
        );
      }
    }
  );


  /*
   * Browser window losing focus.
   */
  window.addEventListener(
    'blur',
    () => {
      recordIntegrityEvent(
        'WINDOW_BLUR'
      );
    }
  );


  /*
   * Fullscreen exit.
   *
   * We only detect this if fullscreen is actually
   * being used. We do not force fullscreen here.
   */
  document.addEventListener(
    'fullscreenchange',
    () => {
      if (
        !document.fullscreenElement
      ) {
        recordIntegrityEvent(
          'FULLSCREEN_EXIT'
        );
      }
    }
  );
}