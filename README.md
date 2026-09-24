# 🛡️ VisionX — Phase 2: AI-Based Fake Identity & Document Screening System
**Smart India Hackathon 2026** | **Problem Statement ID**: SIH26188  
**Theme**: Blockchain & Cybersecurity | **Team**: SixBitss (VisionX)  
**Target Agency**: Sashastra Seema Bal (SSB) / Ministry of Home Affairs

---

## 🌟 What Was Built in Phase 2

### 1. 🔀 4 Complete Input Screening Pipelines
1. **Fixed Structured Data (Aadhaar Card)**:
   * **Real Samples**: Atharv (`0011 0022 0033`), Dhruva (`9876 5432 1002`) $\to$ Valid Verhoeff checksum, authentic national emblem, zero compression boundary halo $\to$ 🟢 **GREEN**.
   * **Fake Samples**: Haroon (`1234 1234 5555`) with counterfeit header typo (`"GOVERNMENT OF INDIYA"`), invalid Verhoeff checksum; John Loyal (`1100 2200 3300`) with photo substitution 5-pixel boundary halo ($\nabla I > 45$) $\to$ 🔴 **RED**.
2. **Unstructured Data (Visas / Permits)**:
   * **Real**: Indian Employment Visa (E-1) $\to$ Consular seal verified, valid through 2028 $\to$ 🟢 **GREEN**.
   * **Fake**: Forged / Expired Entry Visa $\to$ Expired since 2021, synthetic generative text pattern $\to$ 🔴 **RED**.
3. **NFC Digital Chip Reading (e-Passport)**:
   * ISO/IEC 14443 & ICAO Doc 9303 Part 11 DG1 (MRZ), DG2 (Biometric facial photo), and SOD digital signature verification.
   * Compares physical card portrait against cryptographically signed chip face to detect photo swaps.
4. **Offline Regional Metadata Search (Zero-Internet Mode)**:
   * Pre-downloaded encrypted regional package (`north_sector_metadata.json`).
   * Sub-10ms B-Tree query by Primary Key (Aadhaar UID) in remote mountain/Himalayan border checkpoints with deferred sync queue.

---

### 2. 👥 Two-Role Authentication System (RBAC)
* 👮 **Role 1: Border Guard / Checkpoint Terminal**: Handheld mobile PWA view, instant 1-click test suite, live camera scan, NFC tap, offline mode toggle, and sub-2s **GREEN / YELLOW / RED** decision triage.
* 🛡️ **Role 2: Security Officer & Command Dashboard**: Real-time cross-checkpoint monitoring, **SHA-256 Merkle Blockchain Explorer**, DPDP Act 2023 off-chain privacy auditor, and statutory override logging.

---

### 3. 🎨 Authentic Government UI Design
* Built in **Crisp White & Saffron/Deep Orange** (`#EA580C`, `#0F172A`, `#15803D`) following authentic Government of India & SSB portal aesthetics.
* Includes **National Emblem of India**, Tricolor ribbon, official Sector ID tagging, and live sub-2s execution latency progress meter.
* Full **PWA & Web-to-APK** readiness with `manifest.json` and `sw.js`.

---

## 🚀 Quickstart & Running the Prototype

```bash
# 1. Activate Environment
cd /Users/apple/sih_ph2
source ./venv/bin/activate

# 2. Run the Web Server
python3 -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Open **http://127.0.0.1:8000** in your browser or mobile device!
