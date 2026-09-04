/* ==========================================================================
   LIVE EXAMINATION TIMER
   ========================================================================== */

let timerInterval = null;


/**
 * Start a timer using an absolute end timestamp.
 *
 * This prevents a page refresh from simply restarting
 * the full examination duration.
 *
 * The backend will eventually provide the authoritative
 * end time.
 */
function startExamTimer(
  endTime,
  displayElementId,
  onExpireCallback
) {

  const displayElement =
    document.getElementById(
      displayElementId
    );

  const timerBox =
    document.getElementById(
      'timerBox'
    );

  if (!displayElement) {
    return;
  }

  if (timerInterval) {
    clearInterval(timerInterval);
  }


  function update() {

    const remainingMilliseconds =
      new Date(endTime).getTime() -
      Date.now();

    const remainingSeconds =
      Math.max(
        0,
        Math.floor(
          remainingMilliseconds / 1000
        )
      );


    updateTimerDisplay(
      displayElement,
      remainingSeconds
    );


    /*
     * Five-minute warning.
     */
    if (
      remainingSeconds <= 300 &&
      remainingSeconds > 0
    ) {

      if (timerBox) {
        timerBox.classList.add(
          'bg-danger'
        );
      }

      displayElement.classList.add(
        'text-danger',
        'fw-bold'
      );

    } else {

      if (timerBox) {
        timerBox.classList.remove(
          'bg-danger'
        );
      }

      displayElement.classList.remove(
        'text-danger',
        'fw-bold'
      );
    }


    if (remainingSeconds <= 0) {

      clearInterval(timerInterval);

      if (
        typeof onExpireCallback ===
        'function'
      ) {
        onExpireCallback();
      }

    }

  }


  update();

  timerInterval =
    setInterval(
      update,
      1000
    );
}


/**
 * Display remaining seconds.
 */
function updateTimerDisplay(
  element,
  totalSeconds
) {

  if (!element) {
    return;
  }

  const minutes =
    Math.floor(
      totalSeconds / 60
    );

  const seconds =
    totalSeconds % 60;

  element.innerText =
    `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}