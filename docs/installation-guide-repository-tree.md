# Installation Guide & Repository Tree — Excellence Edition

**Architect & Principal Investigator:** Louis-Philippe Audette  
**Affiliation:** Independent Researcher, Goldstream, Langford, BC, Canada  
**Last Updated:** 2026-09-11T00:00:00.000Z  

---

## 1. Overview

This guide provides step-by-step instructions for cloning, setting up, and navigating the PSIVI.COM Open Science Hub repository. The repository is designed for maximum reproducibility, FAIR compliance, and seamless integration with NASA, ESA, and CSA open-science workflows.

**Important:** This repository contains open-source software, open data, and open documentation. Hardware designs and physical implementations are **All Rights Reserved** and managed separately at [w-1-n.com](https://w-1-n.com).

---

## 2. Prerequisites

Before cloning the repository, ensure you have the following installed:

### 2.1 Required Software

| Software | Version | Purpose |
| :--- | :--- | :--- |
| **Git** | 2.30+ | Version control |
| **Python** | 3.10+ | Data processing scripts |
| **Go** | 1.21+ | Tree rendering and automation tools |
| **Node.js** | 18+ (optional) | Jekyll local development |
| **Jekyll** | 4.3+ (optional) | Local website preview |

### 2.2 Recommended Tools

- **VS Code** or **Cursor** — Code editor with Markdown preview
- **GitHub CLI (`gh`)** — Streamlined GitHub workflows
- **jq** — JSON processing for metadata validation
- **tree** — Visualize repository structure

---

## 3. Installation Steps

### 3.1 Clone the Repository

```bash
# Clone via HTTPS
git clone https://github.com/psivicom/psivicom.github.io.git

# Or via GitHub CLI
gh repo clone psivicom/psivicom.github.io

# Navigate into the repository
cd psivicom.github.io
```
3.2 Verify License Compliance after cloning, verify that all license files are present and correctly configured:
