/* ==========================================================================
   LIVE EXAMINATION ENGINE
   Frontend exam state, question navigation and answer management.

   Backend integration is intentionally kept separate.
   This file manages the browser-side examination experience.
   ========================================================================== */

const EXAM_STATE_KEY = 'exam_runtime_state';

let examState = {
  examId: null,
  attemptId: null,

  /*
   * Question metadata required by the frontend.
   *
   * This is currently populated from the static demo HTML.
   * Later, the backend API will provide this data.
   */
  questions: [],

  currentQuestionIndex: 0,

  answers: {},
  reviewQuestions: [],
integrityEvents: [],
startedAt: null,
  endsAt: null,

  isSubmitted: false
};


/* ==========================================================================
   STATE MANAGEMENT
   ========================================================================== */

function loadExamState() {
  const storedState =
    sessionStorage.getItem(EXAM_STATE_KEY);

  if (!storedState) {
    return false;
  }

  try {
    const parsedState =
      JSON.parse(storedState);

    examState = {
      ...examState,
      ...parsedState
    };

    return true;

  } catch (error) {

    console.error(
      'Unable to restore exam state:',
      error
    );

    sessionStorage.removeItem(
      EXAM_STATE_KEY
    );

    return false;
  }
}


function saveExamState() {
  sessionStorage.setItem(
    EXAM_STATE_KEY,
    JSON.stringify(examState)
  );
}
function buildQuestionsFromPage() {

  const cards =
    getQuestionCards();

  return cards.map((card, index) => {

    const questionNumber =
      index + 1;

    const questionText =
      card.querySelector('h5')
        ?.textContent
        .trim() || '';

    const metadata =
      card.querySelector(
        '.text-muted.small'
      )?.textContent || '';

    const parts =
      metadata.split('•');

    const marks =
      parts[0]
        ?.replace('Marks', '')
        .trim() || '';

    const type =
      parts[1]
        ?.trim() || '';

    return {
      number: questionNumber,
      text: questionText,
      marks: marks,
      type: type
    };
  });
}
function initializeQuestions() {

  /*
   * If questions already exist in state,
   * keep them.
   *
   * This is important when the page is refreshed.
   */
  if (
    Array.isArray(examState.questions) &&
    examState.questions.length > 0
  ) {
    return;
  }

  const questions =
    buildQuestionsFromPage();

  if (questions.length === 0) {
    return;
  }

  examState.questions =
    questions;

  saveExamState();
}

function clearExamState() {
  sessionStorage.removeItem(EXAM_STATE_KEY);

 examState = {
  examId: null,
  attemptId: null,

  questions: [],

  currentQuestionIndex: 0,

  answers: {},
  reviewQuestions: [],
integrityEvents: [],
startedAt: null,
  endsAt: null,

  isSubmitted: false
};
}


/* ==========================================================================
   QUESTION DISCOVERY
   ========================================================================== */

function getQuestionCards() {
  return Array.from(
    document.querySelectorAll('.question-card')
  );
}


function getTotalQuestions() {

  if (
    Array.isArray(examState.questions) &&
    examState.questions.length > 0
  ) {
    return examState.questions.length;
  }

  return getQuestionCards().length;
}


function getQuestionNumber(card) {
  const cards = getQuestionCards();

  return cards.indexOf(card) + 1;
}


/* ==========================================================================
   QUESTION NAVIGATION
   ========================================================================== */

function navigateQuestion(index) {

  const cards = getQuestionCards();
  const totalQuestions = cards.length;

  if (
    index < 1 ||
    index > totalQuestions
  ) {
    return;
  }

  cards.forEach(card => {
    card.classList.add('d-none');
  });

  const targetCard = cards[index - 1];

  if (targetCard) {
    targetCard.classList.remove('d-none');
  }

  document
    .querySelectorAll('.question-palette-btn')
    .forEach(button => {
      button.classList.remove('current');
    });

  const paletteButton =
    document.getElementById(
      `palette-btn-${index}`
    );

  if (paletteButton) {
    paletteButton.classList.add('current');
  }

  examState.currentQuestionIndex = index - 1;

  updateQuestionStatuses();
  saveExamState();
}


/* ==========================================================================
   ANSWER MANAGEMENT
   ========================================================================== */

function getQuestionInputs(questionNumber) {

  const card =
    document.getElementById(
      `question-${questionNumber}`
    );

  if (!card) {
    return [];
  }

  return Array.from(
    card.querySelectorAll(
      'input[type="radio"], input[type="checkbox"]'
    )
  );
}


function getInputValue(input, index) {

  /*
   * Backend integration should eventually provide
   * a real option/question-option ID through the
   * input's value or data-option-id attribute.
   *
   * For the current static prototype we use:
   * 1. data-option-id
   * 2. value
   * 3. option index as fallback
   */

  if (input.dataset.optionId) {
    return input.dataset.optionId;
  }

  if (
    input.value &&
    input.value !== 'on'
  ) {
    return input.value;
  }

  return String(index + 1);
}


function readQuestionAnswer(questionNumber) {

  const inputs =
    getQuestionInputs(questionNumber);

  const selectedInputs =
    inputs.filter(input => input.checked);

  if (selectedInputs.length === 0) {
    return null;
  }

  const values = selectedInputs.map(
    (input, index) =>
      getInputValue(input, index)
  );

  /*
   * Radio questions have one answer.
   */
  if (
    inputs.some(
      input => input.type === 'radio'
    )
  ) {
    return values[0];
  }

  /*
   * Checkbox/MSQ questions can have
   * multiple answers.
   */
  return values;
}


function saveQuestionAnswer(questionNumber) {

  const answer =
    readQuestionAnswer(questionNumber);

  if (answer === null) {
    delete examState.answers[questionNumber];
  } else {
    examState.answers[questionNumber] = answer;
  }

  updateQuestionStatuses();
  saveExamState();
}


function markAnswered(questionNumber) {
  saveQuestionAnswer(questionNumber);
}


/* ==========================================================================
   REVIEW FLAGS
   ========================================================================== */

function isMarkedForReview(questionNumber) {
  return examState.reviewQuestions.includes(
    questionNumber
  );
}


function toggleReview(questionNumber) {

  const index =
    examState.reviewQuestions.indexOf(
      questionNumber
    );

  if (index === -1) {
    examState.reviewQuestions.push(
      questionNumber
    );
  } else {
    examState.reviewQuestions.splice(
      index,
      1
    );
  }

  updateQuestionStatuses();
  saveExamState();
}


/* ==========================================================================
   QUESTION STATUS / PALETTE
   ========================================================================== */

function isQuestionAnswered(questionNumber) {

  return Object.prototype.hasOwnProperty.call(
    examState.answers,
    questionNumber
  );
}


function updateQuestionStatuses() {

  const totalQuestions =
    getTotalQuestions();

  for (
    let questionNumber = 1;
    questionNumber <= totalQuestions;
    questionNumber++
  ) {

    const paletteButton =
      document.getElementById(
        `palette-btn-${questionNumber}`
      );

    if (!paletteButton) {
      continue;
    }

    paletteButton.classList.remove(
      'answered',
      'review'
    );

    if (
      isQuestionAnswered(questionNumber)
    ) {
      paletteButton.classList.add(
        'answered'
      );
    }

    if (
      isMarkedForReview(questionNumber)
    ) {
      paletteButton.classList.add(
        'review'
      );
    }
  }

  const currentQuestion =
    examState.currentQuestionIndex + 1;

  document
    .querySelectorAll('.question-palette-btn')
    .forEach(button => {
      button.classList.remove('current');
    });

  const currentButton =
    document.getElementById(
      `palette-btn-${currentQuestion}`
    );

  if (currentButton) {
    currentButton.classList.add('current');
  }
}


/* ==========================================================================
   QUESTION COUNTS
   ========================================================================== */

function getAnsweredCount() {

  return Object.keys(
    examState.answers
  ).length;
}


function getUnansweredCount() {

  return Math.max(
    getTotalQuestions() -
    getAnsweredCount(),
    0
  );
}


function getReviewCount() {

  return examState.reviewQuestions.length;
}


/* ==========================================================================
   SUBMISSION PAYLOAD
   ========================================================================== */

function getSubmissionPayload() {
  return {
    exam_id: examState.examId,
    attempt_id: examState.attemptId,
    answers: examState.answers,
    review_questions: examState.reviewQuestions,
    integrity_events: examState.integrityEvents || [],
    submitted_at: new Date().toISOString()
  };
}


/* ==========================================================================
   AUTO SUBMISSION
   ========================================================================== */

function autoSubmitExam() {

  if (examState.isSubmitted) {
    return;
  }

  examState.isSubmitted = true;
  saveExamState();

  /*
   * This is intentionally a frontend integration point.
   *
   * The actual backend submission request will be
   * connected once the backend endpoint contract exists.
   */

  console.warn(
    'Exam time expired. Submission payload:',
    getSubmissionPayload()
  );

  window.location.href =
    '/exam_runtime/submitted.html';
}


/* ==========================================================================
   INITIALIZATION
   ========================================================================== */

document.addEventListener(
  'DOMContentLoaded',
  () => {

    loadExamState();

const cards =
  getQuestionCards();

if (cards.length === 0) {
  return;
}

initializeQuestions();

    /*
     * Restore selected answers.
     */
    cards.forEach((card, index) => {

      const questionNumber = index + 1;

      const storedAnswer =
        examState.answers[
          questionNumber
        ];

      if (storedAnswer === undefined) {
        return;
      }

      const inputs =
        getQuestionInputs(
          questionNumber
        );

      inputs.forEach((input, inputIndex) => {

        const value =
          getInputValue(
            input,
            inputIndex
          );

        if (Array.isArray(storedAnswer)) {

          input.checked =
            storedAnswer.includes(value);

        } else {

          input.checked =
            storedAnswer === value;

        }

      });
    });


    /*
     * Attach answer listeners.
     */
    cards.forEach((card, index) => {

      const questionNumber =
        index + 1;

      const inputs =
        getQuestionInputs(
          questionNumber
        );

      inputs.forEach(input => {

        input.addEventListener(
          'change',
          () => {
            saveQuestionAnswer(
              questionNumber
            );
          }
        );

      });

    });


    /*
     * Restore current question.
     */
    const restoredIndex =
      examState.currentQuestionIndex + 1;

    navigateQuestion(
      restoredIndex >= 1 &&
      restoredIndex <= cards.length
        ? restoredIndex
        : 1
    );

  }
);