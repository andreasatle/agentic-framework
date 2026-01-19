export function initHelpPopovers(root = document) {
  if (!root) {
    return () => {};
  }

  let activeButton = null;
  let activePopover = null;
  let cleanupListeners = [];

  const removeListeners = () => {
    cleanupListeners.forEach((remove) => remove());
    cleanupListeners = [];
  };

  const closeHelp = () => {
    if (!activeButton) {
      return;
    }
    activeButton.setAttribute("aria-expanded", "false");
    activePopover?.remove();
    activePopover = null;
    activeButton = null;
    removeListeners();
  };

  const positionPopover = (button, popover) => {
    const rect = button.getBoundingClientRect();
    const padding = 6;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const popoverRect = popover.getBoundingClientRect();

    let left = rect.left + window.scrollX;
    let top = rect.bottom + padding + window.scrollY;

    if (left + popoverRect.width > viewportWidth - padding) {
      left = Math.max(padding + window.scrollX, viewportWidth - popoverRect.width - padding + window.scrollX);
    }

    if (top + popoverRect.height > viewportHeight - padding + window.scrollY) {
      top = rect.top - popoverRect.height - padding + window.scrollY;
    }

    popover.style.left = `${left}px`;
    popover.style.top = `${top}px`;
  };

  const openHelp = (button) => {
    const text = button?.dataset?.help?.trim();
    if (!text) {
      return;
    }
    closeHelp();

    activeButton = button;
    activeButton.setAttribute("aria-expanded", "true");
    const popover = document.createElement("div");
    popover.className = "intent-help-popover";
    popover.setAttribute("role", "tooltip");
    popover.textContent = text;
    document.body.appendChild(popover);
    positionPopover(activeButton, popover);
    activePopover = popover;

    const handleDocumentClick = (event) => {
      if (event.target === activeButton) {
        return;
      }
      if (activeButton?.contains(event.target)) {
        return;
      }
      if (activePopover?.contains(event.target)) {
        return;
      }
      closeHelp();
    };

    const handleKeyDown = (event) => {
      if (event.key !== "Escape") {
        return;
      }
      event.preventDefault();
      closeHelp();
    };

    const handleReposition = () => {
      if (activeButton && activePopover) {
        positionPopover(activeButton, activePopover);
      }
    };

    document.addEventListener("click", handleDocumentClick);
    document.addEventListener("keydown", handleKeyDown);
    window.addEventListener("resize", handleReposition);
    window.addEventListener("scroll", handleReposition, true);
    cleanupListeners = [
      () => document.removeEventListener("click", handleDocumentClick),
      () => document.removeEventListener("keydown", handleKeyDown),
      () => window.removeEventListener("resize", handleReposition),
      () => window.removeEventListener("scroll", handleReposition, true),
    ];
  };

  const handleRootClick = (event) => {
    const button = event.target.closest(".intent-help");
    if (!button || !root.contains(button)) {
      return;
    }
    event.preventDefault();
    event.stopPropagation();
    if (activeButton === button) {
      closeHelp();
      return;
    }
    openHelp(button);
  };

  root.addEventListener("click", handleRootClick);

  return () => {
    closeHelp();
    root.removeEventListener("click", handleRootClick);
  };
}
