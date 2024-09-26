# main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os

app = FastAPI()

# Mount static files for front-end
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML page to upload files
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" integrity="" crossorigin="anonymous">
    <title>File Upload</title>
</head>
<body>
<div class="container mt-5">
    <h2>Upload Multiple Files</h2>
    <input type="file" id="fileInput" multiple class="form-control" />
    <button id="uploadButton" class="btn btn-primary mt-3">Upload Files</button>
    <div id="result" class="mt-3"></div>
</div>
<script>
    document.getElementById("uploadButton").onclick = async () => {
        const files = document.getElementById("fileInput").files;
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = ""; // Clear previous results

        if (files.length === 0) {
            resultDiv.innerHTML = "<div class='alert alert-warning'>No files selected.</div>";
            return;
        }

        const uploadPromises = Array.from(files).map(async (file) => {
            const formData = new FormData();
            formData.append("files", file);

            try {
                const response = await fetch("/upload", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Upload failed: ' + response.statusText);
                }
                return await response.text();
            } catch (error) {
                return `Error uploading ${file.name}: ${error.message}`;
            }
        });

        const results = await Promise.all(uploadPromises);
        resultDiv.innerHTML = results.map(r => `<div>${r}</div>`).join("");
    };
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=html_content)

@app.post("/upload/")
async def upload_files(files: List[UploadFile]):
    if not files:
        return "No files uploaded."

    uploaded_files = []
    for file in files:
        # Validate file type
        if not file.filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf')):
            return {"error": f"File type not supported: {file.filename}"}

        # Save file to local directory (for demonstration)
        file_location = os.path.join("static/uploads", file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        uploaded_files.append(file.filename)

    return {"message": f"Successfully uploaded: {', '.join(uploaded_files)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)