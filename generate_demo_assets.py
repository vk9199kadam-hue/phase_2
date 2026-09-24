"""
Generates high-fidelity visual demo assets for the 4 testing pipelines:
1. Fixed ID Aadhaar Cards (Atharv Real, Dhruva Real, Haroon Fake with INDIYA typo, John Loyal Fake with Halo)
2. Unstructured Visas (Employment Visa Real, Expired/Synthetic Visa Fake)
3. e-Passport MRZ & Chip payloads
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "storage", "sample_data")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def create_synthetic_face(name: str, bg_color=(200, 210, 220), shirt_color=(200, 50, 50)) -> Image.Image:
    """Draws a clean passport-style synthetic portrait silhouette"""
    img = Image.new("RGB", (180, 220), bg_color)
    draw = ImageDraw.Draw(img)
    # Head
    draw.ellipse([50, 40, 130, 130], fill=(235, 195, 165), outline=(180, 140, 120), width=2)
    # Hair
    draw.ellipse([46, 30, 134, 80], fill=(40, 30, 25))
    # Eyes
    draw.ellipse([65, 75, 77, 85], fill=(30, 20, 20))
    draw.ellipse([103, 75, 115, 85], fill=(30, 20, 20))
    # Smile/Mouth
    draw.arc([75, 95, 105, 115], start=0, end=180, fill=(150, 50, 50), width=3)
    # Torso/Shirt
    draw.ellipse([20, 140, 160, 260], fill=shirt_color)
    return img

def create_qr_pattern(size=140) -> Image.Image:
    """Generates a mock QR code matrix"""
    np.random.seed(42)
    grid = np.random.choice([0, 255], size=(size, size), p=[0.45, 0.55]).astype(np.uint8)
    # Corner finder patterns
    def add_finder(g, r, c):
        g[r:r+28, c:c+28] = 0
        g[r+4:r+24, c+4:c+24] = 255
        g[r+8:r+20, c+8:c+20] = 0
    add_finder(grid, 4, 4)
    add_finder(grid, 4, size-32)
    add_finder(grid, size-32, 4)
    return Image.fromarray(grid).convert("RGB")

def render_aadhaar_card(name: str, dob: str, gender: str, uid: str, header_text: str, 
                        slogan_text: str, filename: str, is_halo_fake=False, shirt_color=(200, 50, 50)):
    # 800 x 500 ID card canvas
    img = Image.new("RGB", (800, 500), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer Border
    draw.rectangle([10, 10, 790, 490], outline=(180, 180, 180), width=2)
    
    # Tricolor Header Bar
    # Saffron stripe
    draw.rectangle([200, 30, 760, 50], fill=(255, 153, 51))
    # Green stripe
    draw.rectangle([180, 60, 770, 80], fill=(19, 136, 8))
    
    # National Emblem placeholder / Lion Capital box
    draw.rectangle([40, 30, 110, 110], outline=(100, 100, 100), width=2, fill=(245, 245, 245))
    draw.text((48, 60), "EMBLEM", fill=(80, 80, 80))
    # Barcode under emblem
    for i in range(40, 110, 4):
        draw.line([(i, 115), (i, 125)], fill=(0, 0, 0), width=2)

    # Header Hindi / English
    draw.text((320, 32), "भारत सरकार", fill=(0, 0, 0))
    draw.text((260, 60), header_text, fill=(0, 0, 0))

    # Face Portrait
    face_img = create_synthetic_face(name, shirt_color=shirt_color)
    img.paste(face_img, (40, 150))
    
    if is_halo_fake:
        # Draw visible harsh cut-and-paste boundary halo
        draw.rectangle([36, 146, 224, 374], outline=(255, 0, 255), width=3)
        draw.rectangle([38, 148, 222, 372], outline=(0, 255, 255), width=2)

    # Text details
    y_off = 160
    draw.text((250, y_off), "नाम / Name:", fill=(0, 0, 0))
    draw.text((250, y_off + 25), name, fill=(0, 0, 0))
    
    draw.text((250, y_off + 65), "जन्म तारीख / DOB: " + dob, fill=(0, 0, 0))
    draw.text((250, y_off + 95), gender, fill=(0, 0, 0))

    # QR Code
    qr_img = create_qr_pattern(150)
    img.paste(qr_img, (610, 230))

    # UID Digits (Large centered)
    draw.text((250, 340), uid, fill=(0, 0, 0))

    # Red Divider Line
    draw.line([(20, 400), (780, 400)], fill=(180, 0, 0), width=2)

    # Footer Motto
    draw.text((180, 420), slogan_text, fill=(180, 0, 0))

    img.save(os.path.join(SAMPLE_DIR, filename), "PNG")
    print(f"Generated: {filename}")


def generate_all_samples():
    print("Generating demo assets for SIH26188 Phase 2...")
    
    # 1. Aadhaar Real A (Atharv)
    render_aadhaar_card(
        name="atharv",
        dob="04-01-1995",
        gender="Male",
        uid="0011 0022 0033",
        header_text="GOVERNMENT OF INDIA",
        slogan_text="मेरा आधार, मेरी पहचान",
        filename="aadhaar_real_atharv.png",
        is_halo_fake=False,
        shirt_color=(100, 150, 200)
    )

    # 2. Aadhaar Real B (Dhruva)
    render_aadhaar_card(
        name="Dhruva",
        dob="02-03-1993",
        gender="Male",
        uid="9876 5432 1002",
        header_text="GOVERNMENT OF INDIA",
        slogan_text="मेरा आधार, मेरी पहचान",
        filename="aadhaar_real_dhruva.png",
        is_halo_fake=False,
        shirt_color=(40, 40, 40)
    )

    # 3. Aadhaar Fake A (Haroon - Typos: INDIYA & आदमी का अधिकार)
    render_aadhaar_card(
        name="haroon",
        dob="07-03-1990",
        gender="Male",
        uid="1234 1234 5555",
        header_text="GOVERNMENT OF INDIYA",
        slogan_text="आधार - आदमी का अधिकार",
        filename="aadhaar_fake_haroon.png",
        is_halo_fake=False,
        shirt_color=(220, 40, 40)
    )

    # 4. Aadhaar Fake B (John Loyal - Photo Cut-Paste Halo & Typos)
    render_aadhaar_card(
        name="john loyal",
        dob="01-01-1995",
        gender="Male",
        uid="1100 2200 3300",
        header_text="GOVERNMENT OF INDIYA",
        slogan_text="आधार - आदमी का अधिकार",
        filename="aadhaar_fake_john.png",
        is_halo_fake=True,
        shirt_color=(120, 60, 80)
    )

    # 5. Visa Real (Employment Visa)
    v_real = Image.new("RGB", (750, 480), (250, 252, 255))
    d_vr = ImageDraw.Draw(v_real)
    d_vr.rectangle([10, 10, 740, 470], outline=(30, 58, 138), width=3)
    d_vr.text((220, 30), "REPUBLIC OF INDIA — VISA / ENTRY PERMIT", fill=(30, 58, 138))
    d_vr.text((50, 80), "VISA NO: V-IN-982341-A", fill=(0, 0, 0))
    d_vr.text((50, 120), "TYPE: EMPLOYMENT (E-1)", fill=(0, 0, 0))
    d_vr.text((50, 160), "BEARER: RAHUL SHARMA", fill=(0, 0, 0))
    d_vr.text((50, 200), "NATIONALITY: INDIAN", fill=(0, 0, 0))
    d_vr.text((50, 240), "VALID FROM: 01-01-2024   UNTIL: 31-12-2028", fill=(0, 0, 0))
    d_vr.text((50, 280), "ISSUING POST: HIGH COMMISSION OF INDIA", fill=(0, 0, 0))
    # Stamp
    d_vr.ellipse([500, 120, 680, 300], outline=(30, 130, 60), width=4)
    d_vr.text((530, 200), "CONSULAR SEAL\nVERIFIED", fill=(30, 130, 60))
    v_real.save(os.path.join(SAMPLE_DIR, "visa_real_employment.png"), "PNG")
    print("Generated: visa_real_employment.png")

    # 6. Visa Fake (Expired & Tampered)
    v_fake = Image.new("RGB", (750, 480), (255, 245, 245))
    d_vf = ImageDraw.Draw(v_fake)
    d_vf.rectangle([10, 10, 740, 470], outline=(180, 30, 30), width=3)
    d_vf.text((200, 30), "ENTRY CLEARANCE VISA — EXPIRED/FORGED", fill=(180, 30, 30))
    d_vf.text((50, 80), "VISA NO: V-FORGED-009", fill=(0, 0, 0))
    d_vf.text((50, 120), "TYPE: TOURIST (T-1)", fill=(0, 0, 0))
    d_vf.text((50, 160), "BEARER: UNVERIFIED TRAVELER", fill=(0, 0, 0))
    d_vf.text((50, 200), "NATIONALITY: FOREIGN", fill=(0, 0, 0))
    d_vf.text((50, 240), "VALID FROM: 01-01-2019   UNTIL: 12-04-2021 (EXPIRED)", fill=(180, 0, 0))
    d_vf.text((50, 280), "ISSUING POST: SYNTHETIC GENERATIVE STAMP", fill=(180, 0, 0))
    v_fake.save(os.path.join(SAMPLE_DIR, "visa_fake_expired.png"), "PNG")
    print("Generated: visa_fake_expired.png")

if __name__ == "__main__":
    generate_all_samples()
