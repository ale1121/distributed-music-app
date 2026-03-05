let selectedFilter = null

const searchInput = document.getElementById("searchInput");
const searchSuggestions = document.getElementById("searchSuggestions");

function hideSuggestions() {
    searchSuggestions.innerHTML = "";
    searchSuggestions.classList.add("d-none");
}

function renderSuggestions(items) {
    searchSuggestions.innerHTML = "";
    if (!items.length) {
        searchSuggestions.classList.add("d-none");
        return;
    }

    items.forEach(item => {
        const el = document.createElement("a");
        el.className = "list-group-item list-group-item-action d-flex align-items-center gap-3";
        el.innerHTML = `
        <i class="bi fs-5
          ${item.type == 'Song' ? 'bi-music-note' : item.type == 'Album' ? 'bi-disc-fill' : 'bi-star-fill'}"
          style="color: var(--bs-gray-light-6);"></i>
        <div class="pe-2" style="max-width: 430px;">
          <div class="fw-semibold text-truncate">${item.name}</div>
          <div class="text-gray text-truncate small" style="margin-top: -2px;">
            ${item.type}${item.artist ? " • " + item.artist : ""}
          </div>
        </div>`;
        el.href = item.url;
        searchSuggestions.append(el);
    });

    searchSuggestions.classList.remove("d-none")
}

async function updateSuggestions() {
    const searchValue = searchInput.value.trim();

    if (searchValue.length < 3) {
        hideSuggestions();
        return;
    }

    try {
        let url = `/api/search/suggest?q=${encodeURIComponent(searchValue)}`
        if (selectedFilter) {
            url += `&type=${selectedFilter}`;
        }

        const res = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong");

        renderSuggestions(data);
    } catch (err) {
        hideSuggestions();
        console.log("Search preview error: " + err);
    }
}

function debounce(callback, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => callback(...args), delay)
    }
}

searchInput.addEventListener("input", debounce(async () => {
    updateSuggestions();
}, 200))

document.querySelectorAll('input[name="filters"]').forEach(radio => {
    radio.addEventListener("click", (e) => {
        if (selectedFilter == radio.value) {
            radio.checked = false;
            selectedFilter = null;
        } else {
            selectedFilter = radio.value;
        }
        if (searchInput.contains(e.target)) {
            updateSuggestions();
        } else {
            updateResults();
        }
    });
});


const resultsGrid = document.getElementById("resultsGrid");
const noResults = document.getElementById("noResults");

function renderSearchResults(results) {
    noResults.classList.add("d-none");
    resultsGrid.innerHTML = "";
    if (!results.length) {
        resultsGrid.classList.add("d-none");
        noResults.classList.remove("d-none");
        return;
    }

    results.forEach(item => {
        const placeholder = item.type === "Artist"
            ? "/static/assets/placeholder-avatar.webp"
            : "/static/assets/placeholder-cover.webp";
        const el = document.createElement("div");
        el.className = "col";
        el.innerHTML = `
        <a href="${item.url}"
        class="card grid-card p-2 my-2" style="text-decoration: none; width: 200px;">
          <div class="d-flex flex-column align-items-start">
            <img class="${item.type == 'Artist' ? 'rounded-circle' : 'rounded'} mb-2" width="180px"
              src="${item.img}"
              onerror="this.src='${placeholder}'">
            <div class="fw-semibold text-wrap text-break">${item.name}</div>
            <div class="text-gray small">${item.type}</div>
            ${item.type == "Artist"
                ? ''
                : '<div class="text-gray small text-wrap text-break">' + item.artist + ' • ' +
                (item.type == "Album" ? item.year : item.album) + '</div>'}
          </div>
        </a>`
        el.href = item.url;
        resultsGrid.append(el);
    });
    resultsGrid.classList.remove("d-none")
}

document.getElementById("searchForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const searchValue = searchInput.value.trim();
    if (searchValue.length < 3) {
        showErrorToast("Enter at least 3 characters");
        return;
    }

    hideSuggestions();
    updateResults();
});

async function updateResults() {
    hideSuggestions();

    const searchValue = searchInput.value.trim();
    if (searchValue.length < 3) {
        return;
    }

    try {
        let url = `/api/search/results?q=${encodeURIComponent(searchValue)}`
        if (selectedFilter) {
            url += `&type=${selectedFilter}`;
        }

        const res = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong");

        renderSearchResults(data);
    } catch (err) {
        console.log("Search error: " + err);
    }
}

document.addEventListener("click", (e) => {
    if (!searchInput.contains(e.target)) {
        hideSuggestions();
    }
});
