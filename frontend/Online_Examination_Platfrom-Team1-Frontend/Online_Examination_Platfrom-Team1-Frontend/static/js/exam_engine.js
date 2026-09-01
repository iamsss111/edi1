/* ==========================================================================
   LIVE EXAMINATION ENGINE & QUESTION NAVIGATION LOGIC
   ========================================================================== */

let currentQuestionIndex = 1;
const totalQuestions = 2;

function navigateQuestion(index) {
  if (index < 1 || index > totalQuestions) return;

  // Hide all questions
  document.querySelectorAll('.question-card').forEach(card => card.classList.add('d-none'));

  // Show target question
  const targetCard = document.getElementById(`question-${index}`);
  if (targetCard) targetCard.classList.remove('d-none');

  // Update palette active button
  document.querySelectorAll('.question-palette-btn').forEach(btn => btn.classList.remove('current'));
  const activePaletteBtn = document.getElementById(`palette-btn-${index}`);
  if (activePaletteBtn) activePaletteBtn.classList.add('current');

  currentQuestionIndex = index;
}

function markAnswered(qIndex) {
  const paletteBtn = document.getElementById(`palette-btn-${qIndex}`);
  if (paletteBtn && !paletteBtn.classList.contains('review')) {
    paletteBtn.classList.add('answered');
  }
}

function toggleReview(qIndex) {
  const paletteBtn = document.getElementById(`palette-btn-${qIndex}`);
  if (paletteBtn) {
    paletteBtn.classList.toggle('review');
  }
}

function autoSubmitExam() {
  alert('Time has expired! Submitting your exam automatically...');
  window.location.href = '/exam_runtime/submitted.html';
}
