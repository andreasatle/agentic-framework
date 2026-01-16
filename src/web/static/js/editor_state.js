let currentPostId = null;
let currentMarkdown = null;
let suggestedTitleValue = "";
let isEditingContent = false;

export function getCurrentPostId() {
  return currentPostId;
}

export function setCurrentPostId(value) {
  currentPostId = value === null ? null : String(value);
}

export function getCurrentMarkdown() {
  return currentMarkdown;
}

export function setCurrentMarkdown(value) {
  currentMarkdown = value === null ? null : String(value);
}

export function getSuggestedTitleValue() {
  return suggestedTitleValue;
}

export function setSuggestedTitleValue(value) {
  suggestedTitleValue = String(value || "").trim();
}

export function getIsEditingContent() {
  return isEditingContent;
}

export function setIsEditingContent(value) {
  isEditingContent = Boolean(value);
}
