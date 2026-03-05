const imageInput = document.getElementById("imageInput");
const imageName = document.getElementById("imageName");
const imageUploadForm = document.getElementById("imageUploadForm");
const imageUploadBtn = document.getElementById("imageUploadBtn");
const imageSaveBtn = document.getElementById("imageSaveBtn");
const imageCancelBtn = document.getElementById("imageCancelBtn");
const imageRemoveBtn = document.getElementById("imageRemoveBtn");
const confirmDeleteImgBtn = document.getElementById("confirmDeleteImgBtn");
const cancelDeleteImgBtn = document.getElementById("cancelDeleteImgBtn");
const confirmDelete = document.getElementById("confirmDelete");
const image = document.getElementById("image");
const saveImageSpinner = document.getElementById("saveImageSpinner");

imageInput.addEventListener("change", () => {
    if (imageInput.files.length > 0) {
        imageName.textContent = imageInput.files[0].name;
    } else {
        imageName.textContent = "No file chosen";
    }
});

imageUploadBtn.addEventListener("click", () => {
    imageUploadForm.classList.remove("d-none");
    imageUploadBtn.classList.add("disabled");
});

imageCancelBtn.addEventListener("click", () => {
    imageUploadForm.classList.add("d-none");
    imageUploadBtn.classList.remove("disabled");
    imageName.textContent = "No file chosen";
});

imageSaveBtn.addEventListener("click", async () => {
    const file = imageInput.files?.[0];
    if (!file) {
        showErrorToast("Choose an image");
        return;
    }

    const form = new FormData();
    form.append("image", file);

    saveImageSpinner.classList.remove("d-none");

    try {
        const res = await fetch(imageSaveBtn.dataset.uploadUrl, {
            method: "PUT",
            headers: {
                "Accept": "application/json"
            },
            body: form
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong");

        showSuccessToast("Image updated");
        image.src = data["image_url"];
        imageRemoveBtn.classList.remove("d-none");
    } catch (err) {
        showErrorToast(err.message || "Something went wrong");
    } finally {
        saveImageSpinner.classList.add("d-none");
        imageName.textContent = "No file chosen";
        imageUploadForm.classList.add("d-none");
        imageUploadBtn.classList.remove("disabled");
    }
});

imageRemoveBtn.addEventListener("click", () => {
    imageRemoveBtn.classList.add("d-none");
    confirmDelete.classList.remove("d-none");
});

cancelDeleteImgBtn.addEventListener("click", () => {
    imageRemoveBtn.classList.remove("d-none");
    confirmDelete.classList.add("d-none");
})

confirmDeleteImgBtn.addEventListener("click", async () => {
    try {
        const res = await fetch(confirmDeleteImgBtn.dataset.deleteUrl, {
            method: "DELETE",
            headers: {
                "Accept": "application/json"
            }
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.message || "Something went wrong")

        showSuccessToast("Image removed");
        image.src = confirmDeleteImgBtn.dataset.placeholderUrl;
        confirmDelete.classList.add("d-none");
    } catch (err) {
        showErrorToast(err.message || "Something went wrong")
    }
});
