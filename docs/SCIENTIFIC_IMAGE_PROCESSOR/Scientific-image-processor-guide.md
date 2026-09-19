# PSIVI.COM — FAIR Image Processor: User Guide & Compliance Documentation

**Version:** 1.0.0  
**Date:** 2026-09-19  
**Author:** Louis-Philippe Audette, Independent Researcher (Goldstream, Langford, BC)  
**License:** Code: EUPL 1.2 | Documentation: CC BY-SA 4.0  
**Repository:** [psivicom.github.io](https://psivicom.github.io)  

---

## 1. Overview

The **PSIVI FAIR Image Processor** is a client-side, open-source utility designed to prepare scientific imagery for archival in trusted, open-access repositories (e.g., Zenodo, OSF) and for compliance with major space agency mandates (NASA, ESA, CSA, JAXA). 

Unlike conventional image editors, this tool prioritizes **provenance, interoperability, and data sovereignty**. It embeds machine-readable FAIR metadata directly into the image file (via EXIF) while applying non-destructive visual watermarks, ensuring your research remains attributable, auditable, and reproducible without ever leaving your local browser environment.

---

## 2. Scientific Compliance Requirements Met

This tool was explicitly engineered to satisfy the rigorous data management and open science policies of modern research institutions. 

### 🟢 FAIR Data Principles Mapping
| Principle | Implementation in Tool |
| :--- | :--- |
| **Findable** | Enforces entry of a Persistent Identifier (DOI, Handle, or "Unpublished") and Creator name. |
| **Accessible** | Requires explicit selection of a machine-readable license (e.g., CC BY-SA 4.0, CC0). |
| **Interoperable** | Writes metadata to standard EXIF fields (`Artist`, `Copyright`, `ImageDescription`) and embeds a structured JSON payload in the EXIF `UserComment` field for programmatic parsing. |
| **Reusable** | Mandates a detailed scientific description and keywords, ensuring context is preserved for future secondary use. |

### 🟢 Multi-Agency Open Science Mandates
* **NASA TOPS / SPD-41a**: Satisfies requirements for open data licensing, persistent identifiers, and auditable provenance.
* **ESA Open Science Policy**: Aligns with the preference for OSI-approved licenses (EUPL 1.2 for the tool itself) and CC licenses for data products.
* **CSA & JAXA**: Meets baseline FAIR checklist requirements for community data sharing and hardware/software transparency.

### 🟢 NIST SP 800-218 (Secure Software Development Framework)
* **Zero Data Exfiltration**: 100% of image processing, EXIF injection, and compositing occurs locally in the browser via the HTML5 Canvas API and `FileReader`. No data is transmitted to external servers.
* **Supply Chain Security**: Zero external runtime dependencies (except the audited, lightweight `piexifjs` library loaded via trusted CDN). No black-box proprietary code.
* **Domain-Separated Licensing**: The tool’s code is strictly EUPL 1.2, preventing closed-source hijacking while maintaining compatibility with major open-source ecosystems.

---

## 3. Step-by-Step User Guide

### Step 1: Source Image Upload
1. Open the `index.html` file in any modern web browser (Chrome, Firefox, Safari, Edge).
2. Drag and drop your research image into the designated upload area, or click to browse.
   * *Recommendation*: Use **JPEG** or **TIFF** formats, as these natively support robust EXIF metadata embedding. PNG is supported for visual compositing but has limited EXIF support in some viewers.
3. The tool will instantly render a preview. Your image remains strictly on your local machine.

### Step 2: FAIR Metadata Injection
Fill out the metadata form. Fields marked with `*` are enforced by the compliance checker.
* **Creator / Author**: Your full name or ORCID-linked identity (e.g., *Louis-Philippe Audette*).
* **Institution / Affiliation**: Your research group or location (e.g., *PSIVI.COM, Goldstream, Langford BC*).
* **DOI or Persistent Identifier**: The Zenodo DOI (e.g., `10.5281/zenodo.xxxxxx`) or a clear placeholder like `Unpublished-Draft-v1`.
* **License**: Select the appropriate license. For PSIVI data products, **CC BY-SA 4.0** is the standard.
* **Scientific Description**: A concise, reproducible caption. Include methodology, location, and date (e.g., *"RADARSAT-2 backscatter composite of Goldstream watershed, showing soil moisture anomalies correlated with Garry Oak meadow phenology, Sept 2026."*).
* **Keywords**: Comma-separated tags for discoverability (e.g., *SAR-optical fusion, pollinator ecology, Langford*).

### Step 3: Visual Protection (Watermarking)
While EXIF data handles machine readability, visual watermarking deters casual misuse and provides immediate attribution if the image is cropped or shared out of context.
1. **Position**: Select the optimal grid position (default: bottom-right) to avoid obscuring critical scientific data.
2. **Scale**: Adjust the watermark size (10%–50% of image width).
3. **Opacity**: Set transparency (default: 80%) to ensure the watermark is visible but does not interfere with data interpretation (e.g., pixel value analysis).
   * *Note*: The default watermark is a lightweight SVG encoding "PSIVI.COM | CC BY-SA 4.0". 

### Step 4: Validation & Export
1. Click **Validate FAIR Compliance**. The tool will run a real-time audit:
   * ✅ Findable (DOI provided)
   * ✅ Accessible (License specified)
   * ✅ Interoperable (EXIF engine ready)
   * ✅ Reusable (Creator & Description populated)
2. If all checks pass, the **Export JPEG with EXIF** button will activate.
3. Click **Export**. The browser will generate a high-quality JPEG (95% quality), inject the EXIF metadata, composite the watermark, and trigger a local download. 
   * *Filename format*: `FAIR_Image_[DOI_or_Identifier].jpg`

---

## 4. Technical Specifications & Metadata Schema

When you export an image, the tool injects the following EXIF structure. This can be verified using tools like `exiftool` or Python's `piexif`/`Pillow` libraries.

### Standard EXIF Fields (0th IFD)
```text
Artist:                "Louis-Philippe Audette"
Copyright:             "© 2026 Louis-Philippe Audette. CC BY-SA 4.0"
ImageDescription:      "[Your Scientific Description] | DOI: 10.5281/zenodo.xxxxxx | Institution: PSIVI.COM | Keywords: SAR, ecology"
Software:              "PSIVI FAIR Image Tool v1.0 (EUPL 1.2)"
```

### Machine-Readable Payload (Exif IFD)
The `UserComment` field contains an ASCII-prefixed JSON object, allowing automated pipelines (e.g., Zenodo ingestion scripts, NASA PDS tools) to parse metadata without relying on fragile string splitting:
```json
{
  "creator": "Louis-Philippe Audette",
  "institution": "PSIVI.COM, Goldstream, Langford BC",
  "doi": "10.5281/zenodo.xxxxxx",
  "license": "CC BY-SA 4.0",
  "keywords": "RADARSAT, pollinator, Garry Oak, phenology",
  "generated": "2026-09-19T05:11:46.171Z",
  "tool": "PSIVI FAIR Image Processor"
}
```

---

## 5. Best Practices for Zenodo & Repository Submission

1. **Verify Before Uploading**: After exporting, right-click the downloaded file → Properties → Details (Windows) or use `exiftool FAIR_Image.jpg` (macOS/Linux) to confirm the metadata is embedded.
2. **Zenodo Metadata Matching**: Ensure the DOI, creator, and license you enter in this tool *exactly match* the metadata form you fill out on Zenodo. This creates a verifiable chain of custody.
3. **Pre-Publication Embargo**: If the data is under embargo, use the license `"All Rights Reserved (Pre-publication)"` and set the DOI field to `"Embargoed-Pending-DOI"`. The tool will still validate and embed the provenance.
4. **Raw Data Preservation**: Always retain the original, unwatermarked, raw EXIF file in your secure backup. The exported file is the *distribution* copy, not the archival master.

---

## 6. Troubleshooting

| Issue | Resolution |
| :--- | :--- |
| **"EXIF injection failed" alert** | Ensure you are using a modern, updated browser. Some strict privacy extensions (e.g., aggressive Canvas fingerprinting blockers) may interfere with the `canvas.toDataURL()` method. Temporarily disable them for this local file. |
| **Metadata not showing in macOS Preview** | macOS Preview sometimes hides extended EXIF. Use the terminal command `exiftool filename.jpg` or open the file in a dedicated metadata viewer to verify the `UserComment` JSON payload. |
| **Custom Watermark CORS Error** | *Note: The current v1.0 uses a built-in base64 SVG to guarantee zero CORS issues.* If you modify the code to load an external URL, ensure the hosting server sends `Access-Control-Allow-Origin: *` headers, or the canvas will be "tainted" and block export. |

---

## 7. Citation & Attribution

If you use this tool in your research workflow, please cite the PSIVI Open Science Hub:

> Audette, L.-P. (2026). *PSIVI.COM FAIR Image Processor: Client-Side Metadata Injection Tool*. GitHub Repository. https://psivicom.github.io. Licensed under EUPL 1.2.

For questions, data access requests, or collaboration inquiries regarding pollinator monitoring, SAR/optical fusion, or community science infrastructure, please open an issue on GitHub with the tag `data-request` or contact [louis@psivi.com](mailto:louis@psivi.com).

---
*Built as single-file semantic HTML5 for GitHub Pages — Excellence Edition — NASA Blue.*  
*Goldstream, Langford, BC, Canada · Vancouver Island*
