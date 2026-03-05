document.querySelectorAll(".edit-song-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
        const songId = btn.dataset.songId;
        const songTitle = document.getElementById("songTitle" + songId)?.textContent;
        const songPos = parseInt(document.getElementById("songPos" + songId)?.textContent, 10) || 0;

        document.getElementById("editSongCard" + songId)?.classList.remove("d-none");
        document.getElementById("inputSongTitle" + songId).value = songTitle;
        document.getElementById("inputSongPos" + songId).value = songPos;
        document.getElementById("listItem" + songId)?.classList.remove("list-group-item-action");
        btn.classList.add("d-none");
    })
});

document.querySelectorAll(".cancel-edit-song-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
        const songId = btn.dataset.songId;
        document.getElementById("editSongCard" + songId)?.classList.add("d-none");
        document.getElementById("editSongBtn" + songId)?.classList.remove("d-none");
        document.getElementById("listItem" + songId)?.classList.add("list-group-item-action");
    })
});

document.querySelectorAll(".save-edit-song-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
        const songId = btn.dataset.songId;
        const saveUrl = btn.dataset.saveUrl;
        const title = document.getElementById("inputSongTitle" + songId)?.value;
        const pos = parseInt(document.getElementById("inputSongPos" + songId)?.value, 10) || 0;
        if (!title) {
            showErrorToast("Missing song title");
            return;
        }
        const formData = { title: title, position: pos };

        try {
            const res = await fetch(saveUrl, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(formData)
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.message || "Something went wrong");

            document.getElementById("songTitle" + songId).textContent = title;
            document.getElementById("songPos" + songId).textContent = pos;
            document.getElementById("editSongCard" + songId)?.classList.add("d-none");
            document.getElementById("editSongBtn" + songId)?.classList.remove("d-none");
            document.getElementById("listItem" + songId)?.classList.add("list-group-item-action");
            showSuccessToast("Song details updated");
        } catch (err) {
            showErrorToast(err.message || "Something went wrong");
        }
    })
});

document.querySelectorAll(".delete-song-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
        const songId = btn.dataset.songId;
        document.getElementById("confirmDeleteSong" + songId)?.classList.remove("d-none");
        btn.classList.add("d-none");
    })
});

document.querySelectorAll(".cancel-delete-song-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
        const songId = btn.dataset.songId;
        document.getElementById("confirmDeleteSong" + songId)?.classList.add("d-none");
        document.getElementById("deleteSongBtn" + songId)?.classList.remove("d-none");
    })
});


document.querySelectorAll(".confirm-delete-song-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
        const songId = btn.dataset.songId;
        const deleteUrl = btn.dataset.deleteUrl;

        try {
            const res = await fetch(deleteUrl, {
                method: "DELETE",
                headers: {
                    "Accept": "application/json"
                }
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.message || "Something went wrong");

            document.getElementById("listItem" + songId)?.classList.add("d-none");
            document.getElementById("editSongCard" + songId)?.classList.add('d-none');
            showSuccessToast("The song was deleted");
        } catch (err) {
            showErrorToast(err.message || "Something went wrong");
        }
    })
});
