window.showErrorToast = function (msg) {
    const errorToast = document.getElementById("errorToast");
    const errorMsg = document.getElementById("errorToastMsg");
    if (!errorToast || !errorMsg) return;

    errorMsg.textContent = msg || 'Something went wrong';
    bootstrap.Toast.getOrCreateInstance(errorToast).show();
};

window.showSuccessToast = function (msg) {
    const successToast = document.getElementById("successToast");
    const successMsg = document.getElementById("successToastMsg");
    if (!successToast || !successMsg) return;

    successMsg.textContent = msg || 'Done';
    bootstrap.Toast.getOrCreateInstance(successToast).show();
};
