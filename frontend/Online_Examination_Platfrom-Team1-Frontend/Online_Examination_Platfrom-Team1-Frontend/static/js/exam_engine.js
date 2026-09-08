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
  reviewQuestions: []
};


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

    const response = await apiRequest(
      `/exams/${examState.examId}/questions`,
      {
        method: 'GET'
      }
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

    navigateQuestion(0);

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
   ANSWERS
   -------------------------------------------------------------------------- */

async function handleAnswerChange(questionId, optionId) {
  // Update local answer state immediately.
  examState.answers[questionId] = optionId;

  const questionIndex =
    examState.questions.findIndex(
      question => question.exam_question_id === questionId
    );

  if (questionIndex !== -1) {
    markAnswered(questionIndex);
  }

  // Save the answer to the backend.
  try {
    const response = await apiRequest(
      `/attempts/${examState.attemptId}/answers`,
      {
        method: 'POST',
        body: JSON.stringify({
          exam_question_id: questionId,
          selected_option_id: optionId
        })
      }
    );

    console.log('Answer autosaved:', response);
  } catch (error) {
    console.error('Answer autosave failed:', error);

    showToast(
      'Unable to save your answer. Please try again.',
      'danger'
    );
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


function toggleReview(qIndex) {
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

function autoSubmitExam() {
  alert(
    'Time has expired! Submitting your exam automatically...'
  );

  window.location.href =
    '/exam_runtime/submitted.html';
}


/* --------------------------------------------------------------------------
   INITIALIZATION
   -------------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
  initializeExam();
  initializeIntegrityMonitoring();
});