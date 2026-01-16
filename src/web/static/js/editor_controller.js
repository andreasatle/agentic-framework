import { $ } from "./dom.js";
import { closeModal, openModal } from "./modals.js";

export function initEditorController() {
  const titleModal = $("title-modal");
  const authorModal = $("author-modal");

  function openTitleModal() {
    openModal("title-modal", "title-modal-input");
    if (titleModal) {
      titleModal.addEventListener("keydown", handleTitleEscape);
    }
  }

  function closeTitleModal() {
    if (titleModal) {
      titleModal.removeEventListener("keydown", handleTitleEscape);
    }
    closeModal("title-modal");
  }

  function openAuthorModal() {
    openModal("author-modal", "author-modal-input");
    if (authorModal) {
      authorModal.addEventListener("keydown", handleAuthorEscape);
    }
  }

  function closeAuthorModal() {
    if (authorModal) {
      authorModal.removeEventListener("keydown", handleAuthorEscape);
    }
    closeModal("author-modal");
  }

  function handleTitleEscape(event) {
    if (event.key === "Escape") {
      closeTitleModal();
    }
  }

  function handleAuthorEscape(event) {
    if (event.key === "Escape") {
      closeAuthorModal();
    }
  }

  $("open-title-modal-btn")?.addEventListener("click", openTitleModal);
  $("open-author-modal-btn")?.addEventListener("click", openAuthorModal);
  $("title-cancel-btn")?.addEventListener("click", closeTitleModal);
  $("author-cancel-btn")?.addEventListener("click", closeAuthorModal);
}
