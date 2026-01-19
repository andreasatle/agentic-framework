import { $ } from "./dom.js";
import { closeModal, openModal } from "./modals.js";
import { initHelpPopovers } from "./help_popovers.js";

const FIELD_MAP = [
  { key: "document_goal", id: "document-goal", type: "scalar" },
  { key: "audience", id: "audience", type: "scalar" },
  { key: "tone", id: "tone", type: "scalar" },
  { key: "required_sections", id: "required-sections", type: "list" },
  { key: "forbidden_sections", id: "forbidden-sections", type: "list" },
  { key: "must_include", id: "must-include", type: "list" },
  { key: "must_avoid", id: "must-avoid", type: "list" },
  { key: "required_mentions", id: "required-mentions", type: "list" },
  { key: "humor_level", id: "humor-level", type: "scalar" },
  { key: "formality", id: "formality", type: "scalar" },
  { key: "narrative_voice", id: "narrative-voice", type: "scalar" },
];

function escapeYamlString(value) {
  const escaped = value.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  return `"${escaped}"`;
}

function formatScalar(value) {
  if (value.includes("\n")) {
    const indented = value.replace(/\r?\n/g, "\n  ");
    return `|\n  ${indented}`;
  }
  if (/^[A-Za-z0-9 _-]+$/.test(value)) {
    return value;
  }
  return escapeYamlString(value);
}

function serializeIntent(fields) {
  const lines = [];
  fields.forEach(({ key, type, value }) => {
    if (type === "list") {
      if (!value.length) {
        return;
      }
      lines.push(`${key}:`);
      value.forEach((item) => {
        lines.push(`  - ${formatScalar(item)}`);
      });
      return;
    }
    if (!value) {
      return;
    }
    lines.push(`${key}: ${formatScalar(value)}`);
  });
  return lines.join("\n") + "\n";
}

function parseYaml(text) {
  const result = {};
  const lines = text.split(/\r?\n/);
  let currentKey = null;
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line || /^\s*#/.test(line)) {
      continue;
    }
    const listMatch = line.match(/^\s*-\s*(.+)$/);
    if (listMatch && currentKey) {
      const item = listMatch[1].trim();
      result[currentKey].push(unquoteYaml(item));
      continue;
    }
    const match = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (!match) {
      continue;
    }
    const key = match[1];
    let value = match[2] ?? "";
    if (value === "|") {
      const blockLines = [];
      i += 1;
      while (i < lines.length && /^\s{2}/.test(lines[i])) {
        blockLines.push(lines[i].replace(/^\s{2}/, ""));
        i += 1;
      }
      i -= 1;
      result[key] = blockLines.join("\n").trimEnd();
      currentKey = null;
      continue;
    }
    if (value === "") {
      result[key] = [];
      currentKey = key;
      continue;
    }
    if (value === "[]") {
      result[key] = [];
      currentKey = null;
      continue;
    }
    result[key] = unquoteYaml(value);
    currentKey = null;
  }
  return result;
}

function unquoteYaml(value) {
  const trimmed = value.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    return trimmed.slice(1, -1).replace(/\\"/g, '"').replace(/\\\\/g, "\\");
  }
  return trimmed;
}

function collectIntentValues() {
  return FIELD_MAP.map(({ key, id, type }) => {
    const element = $(id);
    if (!element) {
      return { key, type, value: type === "list" ? [] : "" };
    }
    const raw = element.value ?? "";
    if (type === "list") {
      const values = raw
        .split(/\r?\n/)
        .map((item) => item.trim())
        .filter(Boolean);
      return { key, type, value: values };
    }
    return { key, type, value: raw.trim() };
  });
}

function applyIntentValues(values) {
  FIELD_MAP.forEach(({ key, id, type }) => {
    const element = $(id);
    if (!element) {
      return;
    }
    const value = values[key];
    if (type === "list") {
      element.value = Array.isArray(value) ? value.join("\n") : "";
      return;
    }
    element.value = typeof value === "string" ? value : "";
  });
}

export function initCreateEditorController() {
  const form = $("intent-form");
  if (!form) {
    return;
  }
  initHelpPopovers(document.body);

  $("download-intent-btn")?.addEventListener("click", () =>
    openModal("download-intent-modal", "download-intent-filename"),
  );
  $("download-intent-cancel-btn")?.addEventListener("click", () =>
    closeModal("download-intent-modal"),
  );
  $("download-intent-confirm-btn")?.addEventListener("click", () => {
    const filename =
      $("download-intent-filename")?.value?.trim() || "intent.yaml";
    const yaml = serializeIntent(collectIntentValues());
    const blob = new Blob([yaml], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    closeModal("download-intent-modal");
  });

  $("load-intent-btn")?.addEventListener("click", () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".yaml,.yml,text/yaml";
    input.addEventListener("change", async () => {
      const file = input.files?.[0];
      if (!file) {
        return;
      }
      try {
        const text = await file.text();
        const parsed = parseYaml(text);
        applyIntentValues(parsed);
      } catch (error) {
        alert(error instanceof Error ? error.message : "Failed to load intent.");
      }
    });
    input.click();
  });
}
