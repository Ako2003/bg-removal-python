from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse
from rembg import remove
from io import BytesIO
from PIL import Image
import os

app = FastAPI()

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    contents = await file.read()
    output = remove(contents)
    return StreamingResponse(BytesIO(output), media_type="image/png")


@app.post("/test-local")
async def test_local(file: UploadFile = File(...)):
    contents = await file.read()
    output = remove(contents)
    return StreamingResponse(BytesIO(output), media_type="image/png")


@app.post("/add-bg")
async def add_background(
    foreground: UploadFile = File(...),
    background: UploadFile = File(...)
):
    # Read and convert foreground (should have transparency)
    fg_bytes = await foreground.read()
    fg_img = Image.open(BytesIO(fg_bytes)).convert("RGBA")

    # Read and convert background
    bg_bytes = await background.read()
    bg_img = Image.open(BytesIO(bg_bytes)).convert("RGBA")
    bg_img = bg_img.resize(fg_img.size)

    # Composite the images
    combined = Image.alpha_composite(bg_img, fg_img)

    # Save result to buffer and return
    buf = BytesIO()
    combined.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")