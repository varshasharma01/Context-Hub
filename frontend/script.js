function triggerUpload() {
    document.getElementById("pdfFile").click();
}

document.getElementById("pdfFile").addEventListener("change", async function () {
    let file = this.files[0];

    if (!file) return;

    // SHOW PDF PREVIEW
    let fileURL = URL.createObjectURL(file);

    document.getElementById("preview").innerHTML = `
        <iframe src="${fileURL}" width="100%" height="100%"></iframe>
    `;

    // SEND TO BACKEND
    let formData = new FormData();
    formData.append("file", file);

    await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData
    });

    alert("PDF uploaded & processed!");
});


async function askQuery() {
    let query = document.getElementById("query").value;

    let res = await fetch(`http://localhost:8000/query?query=${query}`, {
        method: "POST"
    });

    let data = await res.json();
    document.getElementById("response").innerText = data.answer;
}