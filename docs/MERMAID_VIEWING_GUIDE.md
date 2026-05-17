# Viewing Mermaid Diagrams

Several documentation files in this project use [Mermaid](https://mermaid.js.org/) syntax to create flowcharts and diagrams of the Adventure game's cave system.

## Problem

**Visual Studio's built-in Markdown preview does not render Mermaid diagrams.** You will see the raw Mermaid code instead of a visual diagram.

## Files Containing Mermaid Diagrams

- `docs/Colossal Cave Adventure.md` - Unified overview map
- `maps/adventure-maps-mermaid.md` - Detailed map model
- `docs/discovered-map-mermaid.md` - Auto-discovered game graph

## Solutions

### Option 1: View on GitHub (Easiest)

GitHub automatically renders Mermaid diagrams in Markdown files.

1. Push your changes to GitHub
2. Navigate to the file in the GitHub web interface
3. The diagram renders automatically

**Example:**
```
https://github.com/W1T3H4T/Adventure550/blob/master/docs/Colossal%20Cave%20Adventure.md
```

### Option 2: Use Visual Studio Code

VS Code has excellent Mermaid support via extensions.

**Steps:**
1. Install [Visual Studio Code](https://code.visualstudio.com/) (free)
2. Install extension: **Markdown Preview Mermaid Support**
   - Open VS Code
   - Press `Ctrl+Shift+X` (Extensions)
   - Search for "Markdown Preview Mermaid Support"
   - Install by Matt Bierner
3. Open any `.md` file with Mermaid diagrams
4. Press `Ctrl+Shift+V` for preview

### Option 3: Online Mermaid Live Editor

Copy and paste Mermaid code into an online editor.

**Steps:**
1. Open the `.md` file in any text editor
2. Copy the entire code block between ` ```mermaid ` and ` ``` `
3. Visit: [https://mermaid.live/](https://mermaid.live/)
4. Paste the code into the editor
5. View the rendered diagram
6. Optional: Export as PNG/SVG

### Option 4: Visual Studio Extension

Install a Markdown preview extension for Visual Studio.

**Options:**
- Search Visual Studio Marketplace for "Markdown Editor"
- Try extensions like "Markdown Editor v2" or similar
- Check if they support Mermaid rendering

**Note:** Extension support varies. VS Code (Option 2) is more reliable.

### Option 5: Browser Extension

Use a browser extension to render Mermaid in local file previews.

1. Install Chrome/Edge extension: "Mermaid Diagrams"
2. Save `.md` file
3. Open in browser
4. Extension renders Mermaid automatically

## Alternative: View Static Maps

If you just need to see the cave layout, use the GIF images:

```
maps/
??? adv2-1.gif  - Map 1 (surface and early cave)
??? adv2-2.gif  - Map 2 (main cave, halls, maze)
??? adv2-3.gif  - Map 3 (deeper cave, pits, canyons)
```

These are referenced in `docs/Colossal Cave Adventure.md` with embedded images.

## Recommended Workflow

**For Developers:**
- Use **VS Code** with Mermaid extension for local editing
- Push to **GitHub** for team/public viewing

**For Quick Viewing:**
- Use **mermaid.live** online editor (no installation needed)

**For Documentation:**
- Refer users to **GitHub** links in commit messages
- Keep **GIF maps** as fallback visuals

## Why Use Mermaid?

Despite rendering challenges in Visual Studio, Mermaid offers:

1. **Version Control** - Text-based, easy to diff
2. **Maintainability** - Update diagrams by editing text
3. **GitHub Integration** - Renders beautifully on GitHub
4. **Industry Standard** - Widely supported in modern tools
5. **No Binary Files** - No need to manage image files for simple diagrams

## Learn More

- **Mermaid Docs:** [https://mermaid.js.org/](https://mermaid.js.org/)
- **Mermaid Live Editor:** [https://mermaid.live/](https://mermaid.live/)
- **VS Code Extension:** [Marketplace Link](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)

---

**Bottom Line:** Use VS Code or GitHub to view Mermaid diagrams, or refer to the GIF maps for visual reference.
