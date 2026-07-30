const canonicalResponse = await fetch("./data.json");

if (!canonicalResponse.ok) {
  throw new Error(`Could not load catalog data: ${canonicalResponse.status}`);
}

const canonicalCatalog = await canonicalResponse.json();
const runtimeFile =
  new URLSearchParams(window.location.search).get("runtime") === "local"
    ? "./runtime-data.local.json"
    : "./runtime-data.json";
const runtimeResponse = await fetch(runtimeFile);
const runtimeCatalog = runtimeResponse.ok
  ? await runtimeResponse.json()
  : {
      items: [],
      message:
        "No local snapshot was found. Run npm run catalog:snapshot, then reload this page.",
    };

const collections = {
  canonical: canonicalCatalog.items,
  local: runtimeCatalog.items,
};

const state = {
  query: "",
  type: "all",
  availability: "all",
  runtime: "all",
  source: "all",
  status: "all",
  sort: "featured",
  scope: "canonical",
};

const elements = {
  activeFilters: document.querySelector("#active-filters"),
  availability: document.querySelector("#availability"),
  empty: document.querySelector("#empty"),
  emptyCopy: document.querySelector("#empty-copy"),
  environment: document.querySelector("#environment"),
  resultCount: document.querySelector("#result-count"),
  results: document.querySelector("#results"),
  runtime: document.querySelector("#runtime"),
  scopeNote: document.querySelector("#scope-note"),
  search: document.querySelector("#search"),
  sort: document.querySelector("#sort"),
  source: document.querySelector("#source"),
  status: document.querySelector("#status"),
  template: document.querySelector("#item-template"),
};

const activeItems = () => collections[state.scope];

const runtimeLabel = (runtime) =>
  runtime === "codex" ? "Codex" : runtime === "claude" ? "Claude" : "Unknown";

const matchesRuntime = (item) => {
  if (state.runtime === "all") return true;
  if (state.runtime === "both") return item.runtimes.length === 2;
  return item.runtimes.includes(state.runtime);
};

const matchesAvailability = (item) => {
  if (state.availability === "all") return true;
  if (state.availability === "global") return item.availability === "Global";
  if (state.availability === "project") return item.availability === "Project";
  return item.repository === state.availability.replace(/^repo:/, "");
};

const filteredItems = () => {
  const query = state.query.trim().toLowerCase();
  const filtered = activeItems().filter((item) => {
    const haystack = [
      item.name,
      item.displayName,
      ...(item.pluginIds || []),
      ...(item.installations || []).flatMap((installation) => [
        installation.pluginId,
        installation.runtime,
        installation.delivery,
        installation.state,
        installation.version,
      ]),
      item.description,
      item.sourceLabel,
      item.sourceUrl,
      item.availability,
      item.repository,
      item.invocation,
      item.state,
      item.version,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return (
      (!query || haystack.includes(query)) &&
      (state.type === "all" || item.type === state.type) &&
      matchesAvailability(item) &&
      matchesRuntime(item) &&
      (state.source === "all" || item.source === state.source) &&
      (state.status === "all" || item.state === state.status)
    );
  });

  return filtered.sort((a, b) => {
    if (state.sort === "name") return a.name.localeCompare(b.name);
    if (state.sort === "type") {
      return a.type.localeCompare(b.type) || a.name.localeCompare(b.name);
    }
    if (state.sort === "source") {
      return (
        a.sourceLabel.localeCompare(b.sourceLabel) ||
        a.name.localeCompare(b.name)
      );
    }
    if (state.sort === "state") {
      return a.state.localeCompare(b.state) || a.name.localeCompare(b.name);
    }
    return a.featured - b.featured;
  });
};

const makeTag = (label, className = "") => {
  const span = document.createElement("span");
  span.className = `tag ${className}`.trim();
  span.textContent = label;
  return span;
};

const renderSummary = () => {
  const items = activeItems();
  document.querySelector("#total-count").textContent = items.length;
  document.querySelector("#skill-count").textContent = items.filter(
    (item) => item.type === "skill",
  ).length;
  document.querySelector("#plugin-count").textContent = items.filter(
    (item) => item.type === "plugin",
  ).length;
  document.querySelector("#shared-count").textContent = items.filter(
    (item) => item.runtimes.length === 2,
  ).length;
  document.querySelector(".summary div:first-child span").textContent =
    state.scope === "canonical" ? "In our setup" : "On this Mac";
};

const renderScope = () => {
  const isCanonical = state.scope === "canonical";
  elements.environment.textContent = isCanonical ? "Our setup" : "This Mac";
  elements.scopeNote.textContent = isCanonical
    ? "The setup saved in GitHub and used when configuring a new computer."
    : runtimeCatalog.message;
  document.querySelector(".status-filter").hidden = isCanonical;
  document.querySelector(".availability-filter").hidden = isCanonical;
};

const refreshAvailabilityOptions = () => {
  const repositories = [
    ...new Set(
      runtimeCatalog.items.map((item) => item.repository).filter(Boolean),
    ),
  ].sort();
  elements.availability.replaceChildren(
    new Option("All availability", "all"),
    new Option("All repositories", "global"),
    new Option("Project only", "project"),
    ...repositories.map(
      (repository) => new Option(repository, `repo:${repository}`),
    ),
  );
  elements.availability.value = state.availability;
};

const render = () => {
  const items = activeItems();
  const visible = filteredItems();
  elements.results.replaceChildren();

  visible.forEach((item) => {
    const fragment = elements.template.content.cloneNode(true);
    const article = fragment.querySelector(".item");
    fragment.querySelector("h3").textContent = item.displayName || item.name;
    fragment.querySelector(".kind").textContent =
      item.type === "skill" ? "Skill" : "Plugin";
    const availability = fragment.querySelector(".availability");
    availability.textContent =
      item.availability === "Global"
        ? "All repos"
        : item.repository
          ? `Only ${item.repository}`
          : item.availability;
    availability.classList.add(
      item.availability === "Global" ? "global" : "project",
    );
    fragment.querySelector(".description").textContent = item.description;

    const invocation = fragment.querySelector(".invocation");
    if (item.invocation) {
      invocation.textContent =
        item.invocation === "Automatic" ? "Auto-starts" : "Only when asked";
      invocation.classList.add(item.invocation.toLowerCase());
    } else {
      invocation.remove();
    }

    const status = fragment.querySelector(".state");
    if (state.scope === "local") {
      const statusLabels = { Enabled: "On", Disabled: "Off", Partial: "Mixed" };
      status.textContent = statusLabels[item.state] || item.state;
      status.classList.add(item.state.toLowerCase());
    } else {
      status.remove();
    }

    const path = fragment.querySelector(".path");
    if (item.path) {
      path.textContent = item.path;
      if (item.pathHref === null) {
        path.removeAttribute("href");
      } else {
        path.href = item.pathHref || `../${item.path}`;
      }
    } else {
      path.remove();
    }

    const installationPanel = fragment.querySelector(".installation-panel");
    if (item.installations?.length) {
      const body = installationPanel.querySelector("tbody");
      item.installations.forEach((installation) => {
        const row = document.createElement("tr");
        const app = document.createElement("td");
        const deliveryCell = document.createElement("td");
        const packageCell = document.createElement("td");
        const packageId = document.createElement("code");
        const installationStatus = document.createElement("td");
        const delivery =
          installation.delivery === "managed"
            ? "Managed by Codex"
            : installation.delivery === "runtime"
              ? "Bundled with app"
              : "Marketplace plugin";
        const statusParts = [
          installation.state === "Enabled"
            ? "On"
            : installation.state === "Disabled"
              ? "Off"
              : installation.state,
          installation.version,
        ].filter(Boolean);

        app.textContent = runtimeLabel(installation.runtime);
        deliveryCell.textContent = delivery;
        packageId.textContent = installation.pluginId;
        packageCell.append(packageId);
        installationStatus.textContent =
          statusParts.join(" · ") ||
          (installation.delivery === "managed" ? "Auto-updated" : "Desired");
        row.append(app, deliveryCell, packageCell, installationStatus);
        body.append(row);
      });
    } else {
      installationPanel.remove();
    }

    const runtime = fragment.querySelector(".runtime");
    item.runtimes.forEach((itemRuntime) => {
      runtime.append(makeTag(runtimeLabel(itemRuntime), itemRuntime));
    });
    const source = fragment.querySelector(".source");
    if (item.sourceUrl) {
      const sourceLink = document.createElement("a");
      sourceLink.className = "source-link";
      sourceLink.href = item.sourceUrl;
      sourceLink.target = "_blank";
      sourceLink.rel = "noreferrer";
      sourceLink.textContent = item.sourceLabel;
      sourceLink.setAttribute(
        "aria-label",
        `${item.sourceLabel} source for ${item.displayName || item.name}`,
      );
      source.append(sourceLink);
    } else {
      source.textContent = item.sourceLabel;
    }
    const version = fragment.querySelector(".version");
    if (item.installations?.length) {
      const count = item.installations.length;
      const toggle = document.createElement("button");
      const toggleLabel = document.createElement("span");
      const toggleIcon = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "svg",
      );
      const toggleIconPath = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "path",
      );
      const panelId = `installations-${item.id.replace(/[^a-z0-9-]/gi, "-")}`;
      installationPanel.id = panelId;
      toggle.type = "button";
      toggle.className = "installation-toggle";
      toggleLabel.textContent = `${count} ${count === 1 ? "install" : "installs"}`;
      toggleIcon.classList.add("installation-caret");
      toggleIcon.setAttribute("viewBox", "0 0 12 12");
      toggleIcon.setAttribute("aria-hidden", "true");
      toggleIconPath.setAttribute("d", "M2.5 4.25 6 7.75 9.5 4.25");
      toggleIconPath.setAttribute("fill", "none");
      toggleIconPath.setAttribute("stroke", "currentColor");
      toggleIconPath.setAttribute("stroke-linecap", "round");
      toggleIconPath.setAttribute("stroke-linejoin", "round");
      toggleIconPath.setAttribute("stroke-width", "1.25");
      toggleIcon.append(toggleIconPath);
      toggle.append(toggleLabel, toggleIcon);
      toggle.setAttribute("aria-controls", panelId);
      toggle.setAttribute("aria-expanded", "false");
      toggle.addEventListener("click", () => {
        const expanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!expanded));
        installationPanel.hidden = expanded;
      });
      version.append(toggle);
    } else {
      version.textContent =
        item.version === "Git"
          ? "—"
          : item.version === "Managed"
            ? "Auto-updated"
            : item.version;
    }

    article.dataset.type = item.type;
    elements.results.append(fragment);
  });

  elements.empty.hidden = visible.length > 0;
  elements.results.hidden = visible.length === 0;
  elements.emptyCopy.textContent =
    items.length === 0
      ? runtimeCatalog.message
      : "Try a broader search or clear one of the filters.";
  elements.resultCount.textContent = `${visible.length} of ${items.length}`;
  renderFilterChips();
  renderSummary();
  renderScope();
};

const renderFilterChips = () => {
  elements.activeFilters.replaceChildren();
  const filters = [
    state.query && [
      "Search",
      state.query,
      () => ((state.query = ""), (elements.search.value = "")),
    ],
    state.availability !== "all" && [
      "Availability",
      elements.availability.selectedOptions[0].text,
      () => setSelect("availability", "all"),
    ],
    state.runtime !== "all" && [
      "App",
      elements.runtime.selectedOptions[0].text,
      () => setSelect("runtime", "all"),
    ],
    state.source !== "all" && [
      "Source",
      elements.source.selectedOptions[0].text,
      () => setSelect("source", "all"),
    ],
    state.status !== "all" && [
      "State",
      elements.status.selectedOptions[0].text,
      () => setSelect("status", "all"),
    ],
  ].filter(Boolean);

  filters.forEach(([label, value, clear]) => {
    const button = document.createElement("button");
    const copy = document.createElement("span");
    const dismiss = document.createElement("span");
    button.type = "button";
    button.className = "filter-chip";
    copy.textContent = `${label}: ${value}`;
    dismiss.textContent = "×";
    dismiss.setAttribute("aria-hidden", "true");
    button.append(copy, dismiss);
    button.addEventListener("click", () => {
      clear();
      render();
    });
    elements.activeFilters.append(button);
  });
};

const setSelect = (key, value) => {
  state[key] = value;
  elements[key].value = value;
};

const setPressed = (selector, activeButton) => {
  document.querySelectorAll(selector).forEach((button) => {
    const isActive = button === activeButton;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", isActive ? "true" : "false");
  });
};

const resetFilters = () => {
  state.query = "";
  state.type = "all";
  state.availability = "all";
  state.runtime = "all";
  state.source = "all";
  state.status = "all";
  elements.search.value = "";
  elements.availability.value = "all";
  elements.runtime.value = "all";
  elements.source.value = "all";
  elements.status.value = "all";
  const allButton = document.querySelector('.type-segment[data-type="all"]');
  setPressed(".type-segment", allButton);
};

elements.search.addEventListener("input", (event) => {
  state.query = event.target.value;
  render();
});

["availability", "runtime", "source", "status", "sort"].forEach((key) => {
  elements[key].addEventListener("change", (event) => {
    state[key] = event.target.value;
    render();
  });
});

document.querySelectorAll(".type-segment").forEach((button) => {
  button.addEventListener("click", () => {
    state.type = button.dataset.type;
    setPressed(".type-segment", button);
    render();
  });
});

document.querySelectorAll(".scope-segment").forEach((button) => {
  button.addEventListener("click", () => {
    state.scope = button.dataset.scope;
    resetFilters();
    setPressed(".scope-segment", button);
    render();
  });
});

document.querySelector("#clear-filters").addEventListener("click", () => {
  resetFilters();
  render();
});

document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    elements.search.focus();
  }
});

refreshAvailabilityOptions();
render();
