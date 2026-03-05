document.getElementById("reindexBtn").addEventListener("click", async (e) => {
    try {
        const res = await fetch(e.target.dataset.reindexUrl, {
            method: "POST",
            headers: {
                "Accept": "application/json"
            }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong");
        showSuccessToast("Bulk index successful");
    } catch (err) {
        showErrorToast(err.message || "Something went wrong");
    }
});
