let currentIntent = null;

const intentFields = {
  document_goal: document.getElementById("document-goal"),
  audience: document.getElementById("audience"),
  tone: document.getElementById("tone"),
  required_sections: document.getElementById("required-sections"),
  forbidden_sections: document.getElementById("forbidden-sections"),
  must_include: document.getElementById("must-include"),
  must_avoid: document.getElementById("must-avoid"),
  required_mentions: document.getElementById("required-mentions"),
  humor_level: document.getElementById("humor-level"),
  formality: document.getElementById("formality"),
  narrative_voice: document.getElementById("narrative-voice"),
};

const errorArea = document.getElementById("error-area");

function renderIntent(intent) {
  const s = intent.structural_intent || {};
  const sem = intent.semantic_constraints || {};
  const sty = intent.stylistic_preferences || {};
  intentFields.document_goal.value = s.document_goal || "";
  intentFields.audience.value = s.audience || "";
  intentFields.tone.value = s.tone || "";
  intentFields.required_sections.value = (s.required_sections || []).join("\n");
  intentFields.forbidden_sections.value = (s.forbidden_sections || []).join("\n");
  intentFields.must_include.value = (sem.must_include || []).join("\n");
  intentFields.must_avoid.value = (sem.must_avoid || []).join("\n");
  intentFields.required_mentions.value = (sem.required_mentions || []).join("\n");
  intentFields.humor_level.value = sty.humor_level || "";
  intentFields.formality.value = sty.formality || "";
  intentFields.narrative_voice.value = sty.narrative_voice || "";
}

function setError(message) {
  errorArea.textContent = message || "";
}

function handleIntentFileChange(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) {
    return;
  }
  const reader = new FileReader();
  reader.onload = async () => {
    try {
      const yamlText = reader.result;
      const resp = await fetch("/intent/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ yaml_text: yamlText }),
      });
      if (!resp.ok) {
        const detail = await resp.text();
        setError(detail || "Failed to parse intent.");
        return;
      }
      const data = await resp.json();
      currentIntent = data;
      renderIntent(currentIntent);
      setError("");
    } catch (err) {
      setError(err?.message || "Error loading intent.");
    }
  };
  reader.readAsText(file);
}

function saveIntent() {
  console.log("saveIntent called");
}

function generateDocument() {
  console.log("generateDocument called");
}

function saveDocument() {
  console.log("saveDocument called");
}

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("intent-file");
  if (input) {
    input.addEventListener("change", handleIntentFileChange);
  }
});
