const sendArtistReqBtn = document.getElementById("sendArtistReqBtn");

if (sendArtistReqBtn) sendArtistReqBtn.addEventListener("click", async () => {
    sendArtistReqBtn.disabled = true;

    try {
        const res = await fetch(sendArtistReqBtn.dataset.requestUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong");

        sendArtistReqBtn.textContent = "Request sent";
        showSuccessToast("Request sent");

    } catch (err) {
        sendArtistReqBtn.disabled = false;
        showErrorToast(err.message || "Something went wrong");
    }
});

document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
        const deleteUrl = btn.dataset.deleteUrl;

        try {
            const res = await fetch(deleteUrl, {
                method: "DELETE",
                headers: { "Accept": "application/json" }
            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.message || "Something went wrong");

            btn.closest("tr")?.remove();

            showSuccessToast("Request removed");
        } catch (err) {
            showErrorToast(err.message || "Something went wrong");
        }
    });
});
