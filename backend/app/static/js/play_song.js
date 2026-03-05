document.querySelectorAll(".play-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
        const songId = btn.dataset.songId;
        const songTitle = btn.dataset.songTitle;
        const albumTitle = btn.dataset.albumTitle;
        const albumCover = btn.dataset.albumCover;
        const songViewUrl = btn.dataset.songViewUrl;

        try {
            streamUrl = await getStreamUrl(songId);
        } catch (err) {
            showErrorToast(err.message || "Something went wrong");
        }

        setPlayer({ songId, songTitle, albumTitle, albumCover, songViewUrl, streamUrl });
    });
});
