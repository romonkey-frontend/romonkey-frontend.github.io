/* =================================================================
   ROMonkey — script.js
   Opens one section at a time under the buttons, and reveals
   the Features steps one by one.
   ================================================================= */

const STEP_FIRST_DELAY = 300; // ms before the first Features step appears
const STEP_GAP = 220;         // ms between each following step

const buttons = document.querySelectorAll(".pixel-btn");
const panels = document.querySelectorAll(".panel");
const pressStart = document.getElementById("press-start");
let stepTimers = [];

function openPanel(id) {
  panels.forEach(panel => {
    const open = panel.id === id;
    panel.classList.toggle("is-open", open);
    // Closed sections can't be tabbed into or read by screen readers.
    panel.inert = !open;
  });
  buttons.forEach(button => {
    button.setAttribute("aria-expanded", String(button.dataset.panel === id));
  });
  pressStart.classList.toggle("is-gone", id !== null);

  if (id === "features") revealSteps();
  else resetSteps();
}

function resetSteps() {
  stepTimers.forEach(clearTimeout);
  stepTimers = [];
  document.querySelectorAll("#features .step").forEach(step => step.classList.remove("is-revealed"));
}

function revealSteps() {
  resetSteps();
  document.querySelectorAll("#features .step").forEach((step, i) => {
    stepTimers.push(setTimeout(() => step.classList.add("is-revealed"), STEP_FIRST_DELAY + i * STEP_GAP));
  });
}

buttons.forEach(button => {
  button.addEventListener("click", () => {
    // Clicking the open section's button closes it again.
    const alreadyOpen = button.getAttribute("aria-expanded") === "true";
    openPanel(alreadyOpen ? null : button.dataset.panel);
  });
});

// Let a link like index.html#download open that section directly.
const fromHash = location.hash.slice(1);
if ([...panels].some(panel => panel.id === fromHash)) openPanel(fromHash);
