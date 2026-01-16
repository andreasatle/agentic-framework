import { $ } from "./dom.js";

let lastFocusedElement = null;

function trapFocus(modal, event) {
  if (!modal) return;
  if (event.key !== "Tab") return;
  const focusable = modal.querySelectorAll(
    'button, [href], input, textarea, select, [tabindex]:not([tabindex="-1"])',
  );
  if (!focusable.length) return;
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

export function openModal(modalId, focusId) {
  const modal = $(modalId);
  if (!modal) return;
  lastFocusedElement = document.activeElement;
  modal.hidden = false;
  const focusTarget = focusId ? $(focusId) : null;
  if (focusTarget) {
    focusTarget.focus();
  }
  if (!modal._trapHandler) {
    modal._trapHandler = (event) => trapFocus(modal, event);
  }
  modal.addEventListener("keydown", modal._trapHandler);
}

export function closeModal(modalId) {
  const modal = $(modalId);
  if (!modal) return;
  modal.hidden = true;
  if (modal._trapHandler) {
    modal.removeEventListener("keydown", modal._trapHandler);
  }
  if (lastFocusedElement instanceof HTMLElement) {
    lastFocusedElement.focus();
  }
}
