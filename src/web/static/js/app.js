// JavaScript must never own or cache authoritative data.
// Backend responses and templates are the single source of truth.
import { initEditorController } from "./editor_controller.js";
import { initCreateEditorController } from "./create_editor_controller.js";

function initManualEditorPage() {}

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body?.dataset?.page;
  if (!page) return;

  switch (page) {
    case "blog-editor":
      initEditorController();
      break;
    case "blog-editor-create":
      initCreateEditorController();
      break;
    case "manual-editor":
      initManualEditorPage();
      break;
  }
});
