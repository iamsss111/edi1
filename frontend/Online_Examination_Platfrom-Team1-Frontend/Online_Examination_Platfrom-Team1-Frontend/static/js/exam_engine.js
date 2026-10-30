/* ==========================================================================
   LIVE EXAMINATION ENGINE
   ========================================================================== */

const EXAM_ID = 1;

let examState = {
  examId: EXAM_ID,
  attemptId: null,
  questions: [],
  currentQuestionIndex: 0,
  answers: {},
  reviewQuestions: [],
  adaptiveEnabled: false,
  adaptiveQuestionNumber: 0,
  adaptiveLoading: false,
  adaptiveComplete: false,
  adaptiveCurrentQuestionLoaded: false,
  adaptiveAnswerSavedFor: null,
  adaptiveReviewQuestionIds: [],
  adaptiveSaveVersion: 0
};
const pendingAnswerSaves = new Set();
let autoSubmissionStarted = false;


/* --------------------------------------------------------------------------
   INITIALIZE EXAM
   -------------------------------------------------------------------------- */

async function initializeExam() {
  try {
    const storedAttempt = sessionStorage.getItem('exam_runtime_start');

    if (!storedAttempt) {
      throw new Error(
        'No active examination attempt was found. Please start the exam again.'
      );
    }

    const attempt = JSON.parse(storedAttempt);

    if (!attempt.attempt_id || !attempt.exam_id) {
      throw new Error('The stored examination attempt is invalid.');
    }

    examState.attemptId = attempt.attempt_id;
    examState.examId = attempt.exam_id;
    examState.adaptiveEnabled = attempt.adaptive_enabled === true;
    if (!attempt.ends_at) {
      throw new Error('The examination end time was not provided.');
    }

    if (examState.adaptiveEnabled) {
      initializeAdaptiveHistory();
      renderExamHeader({ title: 'Adaptive Examination', subject: 'Adaptive Mode' });
      await loadNextAdaptiveQuestion(true);
    } else {
      const response = await apiRequest(
        `/exams/${examState.examId}/questions`,
        { method: 'GET' }
      );

      if (
        !response ||
        !response.success ||
        !response.data ||
        !Array.isArray(response.data.questions)
      ) {
        throw new Error(
          'The server returned an invalid examination question response.'
        );
      }

      examState.questions = response.data.questions;

      if (examState.questions.length === 0) {
        throw new Error('No questions are available for this examination.');
      }

      renderExamHeader(response.data);
      renderQuestions();
      renderQuestionPalette();
      await restoreSavedAnswers();
      navigateQuestion(0);
    }

    startExamTimer(attempt.ends_at, 'examTimer', autoSubmitExam);

  } catch (error) {
    console.error('Unable to initialize examination:', error);

    alert(
      error.message ||
      'Unable to load the examination.'
    );

    window.location.href = '/student/dashboard.html';
  }
}


/* --------------------------------------------------------------------------
   ADAPTIVE QUESTION FLOW
   -------------------------------------------------------------------------- */

function adaptiveHistoryStorageKey() {
  return `exam_runtime_adaptive_${examState.attemptId}`;
}

function initializeAdaptiveHistory() {
  const navigationPanel = document.getElementById('questionNavigationPanel');
  navigationPanel?.classList.add('d-none');
  document.querySelector('.row.g-4 > .col-lg-8')?.classList.replace('col-lg-8', 'col-lg-12');

  try {
    const saved = JSON.parse(
      sessionStorage.getItem(adaptiveHistoryStorageKey()) || '{}'
    );
    if (Number(saved.attempt_id) === Number(examState.attemptId)) {
      examState.questions = Array.isArray(saved.questions) ? saved.questions : [];
      examState.adaptiveReviewQuestionIds = Array.isArray(saved.review_question_ids)
        ? saved.review_question_ids
        : [];
    }
  } catch (error) {
    console.warn('Unable to restore adaptive question history:', error);
  }
}

function persistAdaptiveHistory() {
  sessionStorage.setItem(adaptiveHistoryStorageKey(), JSON.stringify({
    attempt_id: examState.attemptId,
    questions: examState.questions,
    review_question_ids: examState.adaptiveReviewQuestionIds
  }));
}

async function loadNextAdaptiveQuestion(restoreCurrentAnswer = false) {
  if (examState.adaptiveLoading || examState.adaptiveComplete) return;
  if (examState.adaptiveCurrentQuestionLoaded) {
    const currentQuestion = examState.questions[examState.currentQuestionIndex];
    if (
      currentQuestion &&
      Number(examState.adaptiveAnswerSavedFor) !== Number(currentQuestion.exam_question_id)
    ) {
      const status = document.getElementById('adaptiveAnswerStatus');
      if (status) status.textContent = 'Save an answer successfully before requesting the next question.';
      return;
    }
  }

  examState.adaptiveLoading = true;
  const nextButton = document.getElementById('adaptiveNextQuestionButton');
  if (nextButton) nextButton.disabled = true;

  try {
    const response = await apiRequest(
      `/attempts/${examState.attemptId}/next-question`,
      { method: 'GET' }
    );
    const data = response?.data;

    if (!response?.success || !data || typeof data.has_next_question !== 'boolean') {
      throw new Error('The server returned an invalid adaptive question response.');
    }

    if (!data.has_next_question) {
      examState.adaptiveComplete = true;
      renderAdaptiveCompletion(data.message);
      return;
    }

    const question = data.question;
    if (!question || !question.exam_question_id || !Array.isArray(question.options)) {
      throw new Error('The server returned an invalid adaptive question.');
    }

    let questionIndex = examState.questions.findIndex(
      item => Number(item.exam_question_id) === Number(question.exam_question_id)
    );
    if (questionIndex === -1) {
      examState.questions.push(question);
      questionIndex = examState.questions.length - 1;
      persistAdaptiveHistory();
    }

    examState.currentQuestionIndex = questionIndex;
    examState.adaptiveQuestionNumber = questionIndex + 1;
    examState.adaptiveAnswerSavedFor = null;
    examState.adaptiveCurrentQuestionLoaded = true;
    renderAdaptiveQuestion(question, questionIndex);
    if (restoreCurrentAnswer) await restoreAdaptiveCurrentAnswer(question);
  } catch (error) {
    const status = document.getElementById('adaptiveAnswerStatus');
    if (status) {
      status.className = 'small mt-3 text-danger';
      status.textContent = error.message || 'Unable to load the next question. Try again.';
    } else {
      const container = document.getElementById('questionsContainer');
      if (container) {
        container.innerHTML = `<div class="glass-card p-4 text-danger" role="alert">${escapeHtml(error.message || 'Unable to load the next question. Refresh to retry.')}</div>`;
      }
    }
    if (nextButton) {
      nextButton.disabled = false;
      nextButton.textContent = 'Retry Next Question';
    }
    console.error('Unable to load adaptive question:', error);
  } finally {
    examState.adaptiveLoading = false;
  }
}

function renderAdaptiveQuestion(question, questionIndex) {
  const container = document.getElementById('questionsContainer');
  if (!container) throw new Error('Question container was not found.');

  const optionsHtml = question.options.map(option => `
    <label class="p-3 rounded border section-bg d-flex align-items-center gap-3 cursor-pointer">
      <input type="radio" name="question_${question.exam_question_id}"
        value="${option.option_id}"
        onchange="handleAnswerChange(${question.exam_question_id}, ${option.option_id})">
      <span class="fw-medium">${escapeHtml(option.option_text)}</span>
    </label>
  `).join('');
  const reviewed = examState.adaptiveReviewQuestionIds.includes(question.exam_question_id);

  container.innerHTML = `
    <div class="glass-card p-4 question-card" id="question-${questionIndex}">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <span class="badge bg-primary fs-6">Question ${examState.adaptiveQuestionNumber}</span>
        <span class="text-muted small">${question.marks} Marks &bull; ${escapeHtml(question.question_type || 'Question')}</span>
      </div>
      <h5 class="fw-bold mb-4 text-dark">${escapeHtml(question.question_text)}</h5>
      <div class="d-flex flex-column gap-3 mb-4">${optionsHtml}</div>
      <div class="d-flex justify-content-between align-items-center border-top pt-3">
        <button id="adaptiveReviewButton" type="button"
          class="btn btn-outline-warning btn-sm ${reviewed ? 'active' : ''}"
          onclick="toggleAdaptiveReview(${question.exam_question_id})">
          <i class="bi bi-bookmark-star"></i> ${reviewed ? 'Marked for Review' : 'Mark for Review'}
        </button>
        <button id="adaptiveNextQuestionButton" type="button" class="btn btn-primary btn-sm"
          onclick="loadNextAdaptiveQuestion()" disabled>
          Next Question &rarr;
        </button>
      </div>
      <div id="adaptiveAnswerStatus" class="small mt-3 text-muted" role="status">Select an answer to continue.</div>
      <button id="adaptiveRetrySaveButton" type="button" class="btn btn-link btn-sm p-0 d-none"
        onclick="retryAdaptiveAnswerSave()">Retry saving answer</button>
    </div>
  `;
}

async function restoreAdaptiveCurrentAnswer(question) {
  try {
    const response = await apiRequest(
      `/attempts/${examState.attemptId}/answers`,
      { method: 'GET' }
    );
    const savedAnswer = response?.data?.answers?.find(
      answer => Number(answer.exam_question_id) === Number(question.exam_question_id)
    );
    if (savedAnswer?.selected_option_id == null) return;

    examState.answers[question.exam_question_id] = savedAnswer.selected_option_id;
    examState.adaptiveAnswerSavedFor = question.exam_question_id;
    const radio = document.querySelector(
      `input[name="question_${question.exam_question_id}"][value="${savedAnswer.selected_option_id}"]`
    );
    if (radio) radio.checked = true;
    const nextButton = document.getElementById('adaptiveNextQuestionButton');
    if (nextButton) nextButton.disabled = false;
    const status = document.getElementById('adaptiveAnswerStatus');
    if (status) status.textContent = 'Your saved answer was restored.';
  } catch (error) {
    console.warn('Unable to restore the current adaptive answer:', error);
  }
}

function renderAdaptiveCompletion(message) {
  const container = document.getElementById('questionsContainer');
  if (!container) return;
  container.innerHTML = `
    <div class="glass-card p-4" role="status">
      <h5 class="fw-bold text-dark">Question sequence complete</h5>
      <p class="text-muted mb-0">${escapeHtml(message || 'You have answered all available adaptive questions. Review your attempt before submitting.')}</p>
    </div>
  `;
}

function toggleAdaptiveReview(questionId) {
  const reviewIds = examState.adaptiveReviewQuestionIds;
  const index = reviewIds.indexOf(questionId);
  if (index === -1) reviewIds.push(questionId);
  else reviewIds.splice(index, 1);
  persistAdaptiveHistory();
  const button = document.getElementById('adaptiveReviewButton');
  const reviewed = reviewIds.includes(questionId);
  if (button) {
    button.classList.toggle('active', reviewed);
    button.innerHTML = `<i class="bi bi-bookmark-star"></i> ${reviewed ? 'Marked for Review' : 'Mark for Review'}`;
  }
}

function retryAdaptiveAnswerSave() {
  const question = examState.questions[examState.currentQuestionIndex];
  if (!question) return;
  const optionId = examState.answers[question.exam_question_id];
  if (optionId != null) return saveAdaptiveAnswer(question.exam_question_id, optionId);
}


/* --------------------------------------------------------------------------
   EXAM HEADER
   -------------------------------------------------------------------------- */

function renderExamHeader(examData) {
  const titleElement = document.getElementById('examTitle');
  const subjectElement = document.getElementById('examSubject');

  if (titleElement && examData.title) {
    titleElement.textContent = examData.title;
  }

  if (subjectElement && examData.subject) {
    subjectElement.textContent = examData.subject;
  }
}


/* --------------------------------------------------------------------------
   QUESTION RENDERING
   -------------------------------------------------------------------------- */

function renderQuestions() {
  const container = document.getElementById('questionsContainer');

  if (!container) {
    throw new Error('Question container was not found.');
  }

  container.innerHTML = '';

  examState.questions.forEach((question, index) => {
    const questionNumber = index + 1;

    const card = document.createElement('div');

    card.className =
      `glass-card p-4 question-card ${index === 0 ? '' : 'd-none'}`;

    card.id = `question-${index}`;

    const optionsHtml = question.options
      .map(option => `
        <label class="p-3 rounded border section-bg d-flex align-items-center gap-3 cursor-pointer">
          <input
            type="radio"
            name="question_${question.exam_question_id}"
            value="${option.option_id}"
            onchange="handleAnswerChange(${question.exam_question_id}, ${option.option_id})"
          >
          <span class="fw-medium">${escapeHtml(option.option_text)}</span>
        </label>
      `)
      .join('');

    card.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-3">
        <span class="badge bg-primary fs-6">
          Question ${questionNumber} of ${examState.questions.length}
        </span>

        <span class="text-muted small">
          ${question.marks} Marks &bull; MCQ
        </span>
      </div>

      <h5 class="fw-bold mb-4 text-dark">
        ${escapeHtml(question.question_text)}
      </h5>

      <div class="d-flex flex-column gap-3 mb-4">
        ${optionsHtml}
      </div>

      <div class="d-flex justify-content-between align-items-center border-top pt-3">
        <button
          class="btn btn-outline-warning btn-sm"
          onclick="toggleReview(${index})"
        >
          <i class="bi bi-bookmark-star"></i>
          Mark for Review
        </button>

        <div>
          ${
            index > 0
              ? `<button
                   class="btn btn-outline-secondary btn-sm me-2"
                   onclick="navigateQuestion(${index - 1})"
                 >
                   &larr; Previous
                 </button>`
              : ''
          }

          ${
            index < examState.questions.length - 1
              ? `<button
                   class="btn btn-primary btn-sm"
                   onclick="navigateQuestion(${index + 1})"
                 >
                   Next Question &rarr;
                 </button>`
              : ''
          }
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}


/* --------------------------------------------------------------------------
   QUESTION NAVIGATION
   -------------------------------------------------------------------------- */

function navigateQuestion(index) {
  if (
    index < 0 ||
    index >= examState.questions.length
  ) {
    return;
  }

  document
    .querySelectorAll('.question-card')
    .forEach(card => card.classList.add('d-none'));

  const targetCard =
    document.getElementById(`question-${index}`);

  if (targetCard) {
    targetCard.classList.remove('d-none');
  }

  document
    .querySelectorAll('.question-palette-btn')
    .forEach(btn => btn.classList.remove('current'));

  const activePaletteBtn =
    document.getElementById(`palette-btn-${index}`);

  if (activePaletteBtn) {
    activePaletteBtn.classList.add('current');
  }

  examState.currentQuestionIndex = index;
}


/* --------------------------------------------------------------------------
   QUESTION PALETTE
   -------------------------------------------------------------------------- */

function renderQuestionPalette() {
  const palette = document.getElementById('questionPalette');

  if (!palette) {
    return;
  }

  palette.innerHTML = '';

  examState.questions.forEach((question, index) => {
    const button = document.createElement('button');

    button.type = 'button';
    button.className =
      `question-palette-btn ${index === 0 ? 'current' : ''}`;

    button.id = `palette-btn-${index}`;

    button.textContent = index + 1;

    button.onclick = () => navigateQuestion(index);

    palette.appendChild(button);
  });
}

/* --------------------------------------------------------------------------
   RESTORE SAVED ANSWERS
   -------------------------------------------------------------------------- */

async function restoreSavedAnswers() {
  try {
    const response = await apiRequest(
      `/attempts/${examState.attemptId}/answers`,
      {
        method: 'GET'
      }
    );

    if (
      !response ||
      !response.success ||
      !response.data ||
      !Array.isArray(response.data.answers)
    ) {
      console.warn('No saved answers were returned.');
      return;
    }

    response.data.answers.forEach(answer => {
      examState.answers[answer.exam_question_id] =
        answer.selected_option_id;

      const radioButton = document.querySelector(
        `input[name="question_${answer.exam_question_id}"][value="${answer.selected_option_id}"]`
      );

      if (radioButton) {
        radioButton.checked = true;
      }

      const questionIndex = examState.questions.findIndex(
        question =>
          question.exam_question_id === answer.exam_question_id
      );

      if (questionIndex !== -1) {
        markAnswered(questionIndex);
      }
    });

    console.log('Saved answers restored:', response.data.answers);

  } catch (error) {
    console.error(
      'Unable to restore saved answers:',
      error
    );
  }
}
/* --------------------------------------------------------------------------
   ANSWERS
   -------------------------------------------------------------------------- */

async function handleAnswerChange(questionId, optionId) {
  // Update local answer state immediately.
  examState.answers[questionId] = optionId;

  if (examState.adaptiveEnabled) {
    await saveAdaptiveAnswer(questionId, optionId);
    return;
  }

  const questionIndex =
    examState.questions.findIndex(
      question => question.exam_question_id === questionId
    );

  if (questionIndex !== -1) {
    markAnswered(questionIndex);
  }

  // Save the answer to the backend.
  const saveOperation = apiRequest(
      `/attempts/${examState.attemptId}/answers`,
      {
        method: 'POST',
        body: JSON.stringify({
          exam_question_id: questionId,
          selected_option_id: optionId
        })
      }
    ).then(response => {
      console.log('Answer autosaved:', response);
    }).catch(error => {
      console.error('Answer autosave failed:', error);
    });

  pendingAnswerSaves.add(saveOperation);
  try {
    await saveOperation;
  } finally {
    pendingAnswerSaves.delete(saveOperation);
  }
}

async function saveAdaptiveAnswer(questionId, optionId) {
  const version = ++examState.adaptiveSaveVersion;
  const nextButton = document.getElementById('adaptiveNextQuestionButton');
  const status = document.getElementById('adaptiveAnswerStatus');
  const retryButton = document.getElementById('adaptiveRetrySaveButton');
  const radios = document.querySelectorAll(`input[name="question_${questionId}"]`);

  if (nextButton) nextButton.disabled = true;
  if (retryButton) retryButton.classList.add('d-none');
  if (status) {
    status.className = 'small mt-3 text-muted';
    status.textContent = 'Saving your answer…';
  }
  radios.forEach(radio => { radio.disabled = true; });

  const saveOperation = apiRequest(
    `/attempts/${examState.attemptId}/answers`,
    {
      method: 'POST',
      body: JSON.stringify({
        exam_question_id: questionId,
        selected_option_id: optionId
      })
    }
  );
  pendingAnswerSaves.add(saveOperation);

  try {
    const response = await saveOperation;
    if (!response?.success) {
      throw new Error(response?.message || 'The server did not confirm the answer save.');
    }
    if (version === examState.adaptiveSaveVersion) {
      examState.adaptiveAnswerSavedFor = questionId;
      if (nextButton) nextButton.disabled = false;
      if (status) {
        status.className = 'small mt-3 text-success';
        status.textContent = 'Answer saved. You can continue to the next question.';
      }
    }
  } catch (error) {
    if (version === examState.adaptiveSaveVersion) {
      examState.adaptiveAnswerSavedFor = null;
      if (status) {
        status.className = 'small mt-3 text-danger';
        status.textContent = error.message || 'Answer could not be saved. Retry before continuing.';
      }
      if (retryButton) retryButton.classList.remove('d-none');
    }
    console.error('Adaptive answer autosave failed:', error);
  } finally {
    radios.forEach(radio => { radio.disabled = false; });
    pendingAnswerSaves.delete(saveOperation);
  }
}


function markAnswered(qIndex) {
  const paletteBtn =
    document.getElementById(`palette-btn-${qIndex}`);

  if (
    paletteBtn &&
    !paletteBtn.classList.contains('review')
  ) {
    paletteBtn.classList.add('answered');
  }
}


/* --------------------------------------------------------------------------
   MARK FOR REVIEW
   -------------------------------------------------------------------------- */

function toggleReview(qIndex) {
  if (examState.adaptiveEnabled) {
    const question = examState.questions[qIndex];
    if (question) toggleAdaptiveReview(question.exam_question_id);
    return;
  }

  const paletteBtn =
    document.getElementById(`palette-btn-${qIndex}`);

  if (paletteBtn) {
    paletteBtn.classList.toggle('review');
  }
}


/* --------------------------------------------------------------------------
   HTML ESCAPING
   -------------------------------------------------------------------------- */

function escapeHtml(value) {
  const div = document.createElement('div');
  div.textContent = value ?? '';
  return div.innerHTML;
}


/* --------------------------------------------------------------------------
   AUTO SUBMIT
   -------------------------------------------------------------------------- */

async function autoSubmitExam() {
  if (autoSubmissionStarted || !examState.attemptId) {
    return;
  }
  autoSubmissionStarted = true;

  alert(
    'Time has expired! Submitting your exam automatically...'
  );

  // Let any final autosave finish before locking the attempt.
  await Promise.allSettled([...pendingAnswerSaves]);

  try {
    await apiRequest(
      `/attempts/${examState.attemptId}/submit`,
      { method: 'POST' }
    );
    window.location.href = '/exam_runtime/submitted.html';
  } catch (error) {
    const message = error?.data?.message || '';
    if (/expired|already been submitted/i.test(message)) {
      window.location.href = '/exam_runtime/submitted.html';
      return;
    }
    autoSubmissionStarted = false;
    alert('Automatic submission could not reach the server. Please keep this page open and retry submission.');
  }
}


/* --------------------------------------------------------------------------
   INITIALIZATION
   -------------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
  initializeExam();
  initializeIntegrityMonitoring();
});
