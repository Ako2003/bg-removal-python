from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from io import BytesIO
from PIL import Image, ImageFilter  # ✅ Make sure this is here
import os


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://bg-removal-frontend-axjr.vercel.app",  # ✅ Exact frontend domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    contents = await file.read()
    output = remove(contents)
    return StreamingResponse(BytesIO(output), media_type="image/png")


# @app.get("/test-local", response_class=HTMLResponse)
# async def test_local():
#     image_path = "mae-mu-vbAEHCrvXZ0-unsplash.jpg"

#     if not os.path.exists(image_path):
#         return HTMLResponse("<h2>Image not found.</h2>", status_code=404)

#     with open(image_path, "rb") as f:
#         contents = f.read()

#     output = remove(contents)
#     return StreamingResponse(BytesIO(output), media_type="image/png")


@app.post("/add-bg")
async def add_background(file: UploadFile = File(...)):
    # Load transparent image
    contents = await file.read()
    transparent_img = Image.open(BytesIO(contents)).convert("RGBA")

    # Create white background image
    background = Image.new("RGBA", transparent_img.size, (255, 255, 255, 255))

    # Composite the transparent image over the background
    combined = Image.alpha_composite(background, transparent_img)

    # Save to output_image.png
    output_path = "img/output_image.png"
    combined.convert("RGB").save(output_path, format="PNG")

    # Also return it as response
    buf = BytesIO()
    combined.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")


@app.post("/blur-bg")
async def blur_background(file: UploadFile = File(...)):
    # Step 1: Read and open the uploaded image
    contents = await file.read()
    original_img = Image.open(BytesIO(contents)).convert("RGB")

    # Step 2: Remove background to get foreground with transparency
    foreground_bytes = remove(contents)
    foreground = Image.open(BytesIO(foreground_bytes)).convert("RGBA")

    # Step 3: Create blurred version of original image
    blurred_bg = original_img.filter(ImageFilter.GaussianBlur(radius=15)).convert("RGBA")

    # Step 4: Composite foreground on top of blurred background
    result = Image.alpha_composite(blurred_bg, foreground)

    # Step 5: Return image
    buf = BytesIO()
    result.convert("RGB").save(buf, format="JPEG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")

# @app.get("/test-blur", response_class=StreamingResponse)
# async def test_blur():
#     image_path = "andrew-milko-LspK43UdFo4-unsplash.jpg"

#     if not os.path.exists(image_path):
#         return HTMLResponse("<h2>Image not found.</h2>", status_code=404)

#     # Load original image
#     with open(image_path, "rb") as f:
#         contents = f.read()
#     original_img = Image.open(BytesIO(contents)).convert("RGB")

#     # Remove background to get transparent foreground
#     foreground_bytes = remove(contents)
#     foreground = Image.open(BytesIO(foreground_bytes)).convert("RGBA")

#     # Create blurred background
#     blurred_bg = original_img.filter(ImageFilter.GaussianBlur(radius=15)).convert("RGBA")

#     # Composite foreground over blurred background
#     result = Image.alpha_composite(blurred_bg, foreground)

#     # Return image
#     buf = BytesIO()
#     result.convert("RGB").save(buf, format="JPEG")
#     buf.seek(0)

#     return StreamingResponse(buf, media_type="image/jpeg")

# custom port
