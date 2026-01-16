import { $ } from "./dom.js";
import { closeModal, openModal } from "./modals.js";

export function initEditorController() {
  $("open-title-modal-btn")?.addEventListener("click", () =>
    openModal("edit-title-modal", "edit-title-input"),
  );
  $("open-author-modal-btn")?.addEventListener("click", () =>
    openModal("edit-author-modal", "edit-author-input"),
  );
  $("edit-title-cancel-btn")?.addEventListener("click", () =>
    closeModal("edit-title-modal"),
  );
  $("edit-author-cancel-btn")?.addEventListener("click", () =>
    closeModal("edit-author-modal"),
  );
}
