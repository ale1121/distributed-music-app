const saveAlbumDetailsBtn = document.getElementById("saveAlbumDetailsBtn");

saveAlbumDetailsBtn.addEventListener("click", async () => {
    const title = document.getElementById("inputAlbumTitle").value;
    const yearRaw = document.getElementById("inputAlbumYear").value;
    if (!title) {
        showErrorToast("Missing album title");
        return;
    }
    if (!yearRaw) {
        showErrorToast("Missing release year");
        return;
    }
    year = parseInt(yearRaw, 10) || 0;
    const formData = {
        title: title,
        release_year: year
    };

    try {
        const res = await fetch(saveAlbumDetailsBtn.dataset.saveUrl, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(formData)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong");

        document.getElementById("albumTitle").textContent = title;
        showSuccessToast("Album details updated");

    } catch (err) {
        showErrorToast(err.message || "Something went wrong");
    }
});

const publishAlbumBtn = document.getElementById("publishAlbumBtn");

if (publishAlbumBtn) publishAlbumBtn.addEventListener("click", async () => {
    try {
        const res = await fetch(publishAlbumBtn.dataset.publishUrl, {
            method: "POST",
            headers: {
                "Accept": "application/json"
            }
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong");

        document.getElementById("publishedStatusBadge").innerHTML = `Published <i class="bi bi-globe-americas"></i>`;
        publishAlbumBtn.classList.add("d-none");
        document.getElementById("viewAlbumBtn").classList.remove("d-none");

        showSuccessToast("Album published");
    } catch (err) {
        showErrorToast(err.message || "Something went wrong");
    }
});

const deleteAlbumBtn = document.getElementById("deleteAlbumBtn");
const confirmDeleteAlbum = document.getElementById("confirmDeleteAlbum");
const cancelDeleteAlbumBtn = document.getElementById("cancelDeleteAlbumBtn");

deleteAlbumBtn.addEventListener("click", () => {
    confirmDeleteAlbum.classList.remove("d-none");
    deleteAlbumBtn.classList.add("d-none");
});

cancelDeleteAlbumBtn.addEventListener("click", () => {
    confirmDeleteAlbum.classList.add("d-none");
    deleteAlbumBtn.classList.remove("d-none");
});
