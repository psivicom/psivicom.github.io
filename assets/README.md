# fonts and icons in this website have to be secure and fast to load

The "Gold Standard" Architecture:

Assets: All icons stored as raw SVGs in a /assets/icons/ folder during development.
Production: A build script (like Vite, Webpack, or a simple Python script) inlines those SVGs into the HTML or bundles them into a single sprite.svg file.

Since your website is hosted on **GitHub Pages** (`psivicom.github.io`), you are likely using a static site structure. GitHub Pages does not run a backend server, so you cannot use a "live" build script on the server. 

Instead, you have two choices: a **Manual Workflow** (simple, no extra tools) or an **Automated Workflow** (using GitHub Actions). I recommend starting with the Manual Workflow to ensure it works, then automating it.

Here is the guide to implementing the Gold Standard architecture.

---

### Phase 1: The Asset Structure (Development)
Organize your repository so that your source icons are separated from your production code.

**Repository Folder Structure:**
```text
/ (root)
├── index.html
├── /assets
│   ├── /css
│   └── /icons          <-- Source folder (RAW SVGs)
│       ├── rocket.svg
│       ├── satellite.svg
│       └── globe.svg
└── /dist               <-- (Optional) Production folder
    └── sprite.svg      <-- Generated sprite file
```

**Important:** When saving your `.svg` files, remove the `width` and `height` attributes and replace them with a `viewBox="0 0 24 24"`. This allows you to control the size via CSS.

---

### Phase 2: Implementation Options

#### Option A: The Manual "Sprite" Method (Fast & Secure)
If you don't want to set up complex build tools, you can create your own sprite file manually.

1.  Create a file at `/assets/icons/sprite.svg`.
2.  Wrap every icon in a `<symbol>` tag with a unique `id`.

**Example `sprite.svg`:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <symbol id="icon-rocket" viewBox="0 0 24 24">
    <path d="M...paste rocket path here..."></path>
  </symbol>
  <symbol id="icon-globe" viewBox="0 0 24 24">
    <path d="M...paste globe path here..."></path>
  </symbol>
</svg>
```

**How to use it in your HTML:**
```html
<!-- This is the fastest way to load an icon from a file -->
<svg class="site-icon">
  <use xlink:href="assets/icons/sprite.svg#icon-rocket"></use>
</svg>
```

#### Option B: The Inline Method (Absolute Fastest)
For your most important icons (Logo, Menu, Search), simply paste the `<svg>` code directly into your `index.html`.

```html
<nav>
  <a href="/" class="logo">
    <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
       <path d="M..."></path>
    </svg>
    PSIVICOM
  </a>
</nav>
```

---

### Phase 3: Styling for a "Space Agency" Look
To make these SVGs look professional and consistent, add this to your CSS:

```css
/* Base style for all icons */
.site-icon {
  width: 24px;
  height: 24px;
  fill: currentColor; /* This makes the icon inherit the text color */
  vertical-align: middle;
  transition: fill 0.2s ease;
}

/* Hover effect for interactivity */
.site-icon:hover {
  fill: #005eff; /* Example Space Blue */
}
```

---

### Phase 4: Automation (The "Pro" Step)
Since you are on GitHub, you can use **GitHub Actions** to automatically turn your folder of individual SVGs into a single `sprite.svg` every time you push code.

1.  Create a folder: `.github/workflows/`
2.  Create a file: `build-icons.yml`
3.  Use a simple script (like `svg-sprite` from NPM) to merge the files.

**Simplified Logic for the Action:**
*   **Trigger:** Push to `main` branch.
*   **Action:** Run `npm install -g svg-sprite`, then run `svg-sprite --symbol --sprite assets/icons/*.svg`.
*   **Result:** It generates the `sprite.svg` and commits it back to your repository automatically.

### Final Checklist for `psivicom.github.io`:
1. [ ] **Remove FontAwesome/Ionicons** links from your `<head>`.
2. [ ] **Create `/assets/icons/`** and add your chosen open-source SVGs (from Lucide or Material).
3. [ ] **Convert** them to `<symbol>` tags in a `sprite.svg` or paste them **inline**.
4. [ ] **Update CSS** to use `fill: currentColor` for easy theme changes.
5. [ ] **Push to GitHub** and verify that no external requests are being made to font servers.
