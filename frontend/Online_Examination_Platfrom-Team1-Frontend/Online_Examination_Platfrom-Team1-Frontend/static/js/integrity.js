/*
 * Browser Integrity Monitoring
 *
 * Frontend responsibilities:
 * - Detect tab switching
 * - Detect window focus loss
 * - Detect fullscreen exit
 * - Report integrity events to the backend
 * - Show the current violation count
 * - Redirect after backend auto-submission
 *
 * The backend remains authoritative for exam integrity.
 */

const INTEGRITY_EVENT_COOLDOWN = 1500;

let lastIntegrityEventTime = 0;
let integrityAutoSubmitTriggered = false;


function createIntegrityEvent(type, metadata = {}) {
  return {
    type,
    occurred_at: new Date().toISOString(),
    metadata
  };
}


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

  if (integrityAutoSubmitTriggered) {
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

    console.log(
      'Integrity event recorded:',
      response
    );

    if (
      response &&
      response.success &&
      response.data
    ) {
      const violationCount =
        response.data.violation_count;

      const autoSubmitTriggered =
        response.data.auto_submit_triggered;

      if (
        typeof violationCount === 'number'
      ) {
        showIntegrityWarning(
          event,
          violationCount
        );
      }

      if (autoSubmitTriggered) {
        integrityAutoSubmitTriggered = true;

        showAutoSubmitWarning();

        setTimeout(() => {
          window.location.href =
            '/exam_runtime/submitted.html';
        }, 1500);
      }
    }

  } catch (error) {

    console.error(
      'Failed to record integrity event:',
      error
    );

    /*
     * If the backend says the examination has already
     * been submitted, stop sending further events.
     */
    if (
      error &&
      error.message &&
      error.message.includes(
        'after the examination is submitted'
      )
    ) {
      integrityAutoSubmitTriggered = true;
    }
  }
}


function recordIntegrityEvent(
  type,
  metadata = {}
) {
  if (typeof examState === 'undefined') {
    return;
  }

  if (integrityAutoSubmitTriggered) {
    return;
  }

  const now = Date.now();

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

  /*
   * Backend response is authoritative for
   * violation count and auto-submission.
   */
  sendIntegrityEvent(event);
}


function getIntegrityMessage(
  type,
  violationCount
) {
  let message;

  switch (type) {

    case 'TAB_SWITCH':
      message =
        'You left the exam tab. Please return to the examination window.';
      break;

    case 'WINDOW_BLUR':
      message =
        'The examination window lost focus. Please return to the exam.';
      break;

    case 'FULLSCREEN_EXIT':
      message =
        'Fullscreen mode was exited. Please return to fullscreen mode if required.';
      break;

    default:
      message =
        'An examination environment change was detected.';
  }

  if (
    typeof violationCount === 'number'
  ) {
    message += `<br><strong>Integrity violations: ${violationCount}/3</strong>`;
  }

  return message;
}


function showIntegrityWarning(
  event,
  violationCount
) {
  const existingWarning =
    document.getElementById(
      'integrityWarning'
    );

  if (existingWarning) {
    existingWarning.remove();
  }

  const warning =
    document.createElement('div');

  warning.id =
    'integrityWarning';

  warning.className =
    'alert alert-warning position-fixed top-0 start-50 translate-middle-x mt-3 shadow';

  warning.style.zIndex = '9999';
  warning.style.maxWidth = '90%';

  warning.innerHTML = `
    <strong>Exam Integrity Notice</strong><br>
    ${getIntegrityMessage(
      event.type,
      violationCount
    )}
  `;

  document.body.appendChild(
    warning
  );

  setTimeout(() => {
    warning.remove();
  }, 5000);
}


function showAutoSubmitWarning() {
  const existingWarning =
    document.getElementById(
      'integrityWarning'
    );

  if (existingWarning) {
    existingWarning.remove();
  }

  const warning =
    document.createElement('div');

  warning.id =
    'integrityWarning';

  warning.className =
    'alert alert-danger position-fixed top-0 start-50 translate-middle-x mt-3 shadow';

  warning.style.zIndex = '9999';
  warning.style.maxWidth = '90%';

  warning.innerHTML = `
    <strong>Exam Automatically Submitted</strong><br>
    Maximum integrity violations reached.<br>
    Your examination has been submitted.
  `;

  document.body.appendChild(
    warning
  );
}


function initializeIntegrityMonitoring() {
  if (typeof examState === 'undefined') {
    return;
  }

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

  window.addEventListener(
    'blur',
    () => {
      recordIntegrityEvent(
        'WINDOW_BLUR'
      );
    }
  );

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