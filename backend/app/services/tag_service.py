import io
import qrcode
import barcode
from barcode.writer import ImageWriter
from PIL import Image
from pathlib import Path
from app.core.config import settings


def generate_qr_code(data: str, output_path: str) -> str:
    """Generate QR code image and save to disk."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    return output_path


def generate_barcode(tag_code: str, output_path: str) -> str:
    """Generate Code128 barcode image and save to disk."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    code128 = barcode.get("code128", tag_code, writer=ImageWriter())
    # Save without extension — barcode lib adds .png
    base_path = output_path.replace(".png", "")
    saved = code128.save(base_path)
    return saved


def compress_image(input_path: str, output_path: str, max_kb: int = None) -> str:
    """Compress ornament photo to target KB size."""
    target_kb = max_kb or settings.MAX_IMAGE_SIZE_KB
    img = Image.open(input_path)
    img = img.convert("RGB")

    quality = 90
    while quality > 10:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        size_kb = buffer.tell() / 1024
        if size_kb <= target_kb:
            break
        quality -= 10

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())
    return output_path


def generate_tag_assets(tag_code: str, ornament_id: str) -> dict:
    """Generate both QR and barcode for an ornament tag."""
    base_dir = Path(settings.UPLOAD_DIR) / "tags" / ornament_id
    qr_path = str(base_dir / "qr.png")
    barcode_path = str(base_dir / "barcode")

    generate_qr_code(tag_code, qr_path)
    saved_barcode = generate_barcode(tag_code, barcode_path + ".png")

    return {
        "qr_path": qr_path,
        "barcode_path": saved_barcode,
    }
