const addSongBtn = document.getElementById("addSongBtn");
const newSongCard = document.getElementById("newSongCard");
const newSongTitleInput = document.getElementById("newSongTitleInput");
const newSongFileName = document.getElementById("newSongFileName");
const newSongPosInput = document.getElementById("newSongPosInput");
const newSongFileInput = document.getElementById("newSongFileInput");
const newSongCancelBtn = document.getElementById("newSongCancelBtn");
const newSongSaveBtn = document.getElementById("newSongSaveBtn");

addSongBtn.addEventListener("click", () => {
    newSongCard.classList.remove("d-none");
});

newSongCancelBtn.addEventListener("click", () => {
    newSongTitleInput.value = null;
    newSongFileName.value = null;
    newSongPosInput.value = 0;
    newSongCard.classList.add("d-none");
});

newSongFileInput.addEventListener("change", () => {
    if (newSongFileInput.files.length > 0) {
        newSongFileName.value = newSongFileInput.files[0].name;
    } else {
        newSongFileName.value = null;
    }
});

newSongSaveBtn.addEventListener("click", async (e) => {
    e.preventDefault();

    const title = newSongTitleInput.value;
    const file = newSongFileInput.files?.[0];
    const pos = parseInt(newSongPosInput.value, 10) || 0;
    if (!title) {
        showErrorToast("Missing song title");
        return;
    }
    if (!file) {
        showErrorToast("Missing audio file");
        return;
    }

    const form = new FormData();
    form.append("title", title);
    form.append("audio", file);
    form.append("position", pos);

    try {
        const res = await fetch(newSongSaveBtn.dataset.saveUrl, {
            method: "POST",
            headers: {
                "Accept": "application/json"
            },
            body: form
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong");

        showSuccessToast("Song added");
        location.reload();

    } catch (err) {
        showErrorToast(err.message || "Something went wrong");
    }
});
