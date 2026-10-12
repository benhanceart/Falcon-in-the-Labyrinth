import os
import html
import urllib.parse
from pathlib import Path

# Media extension definitions
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
AUDIO_EXTS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac'}
VIDEO_EXTS = {'.mp4', '.webm', '.mov', '.m4v'}
TEXT_EXTS  = {'.txt', '.md'}
HERO_NAMES = {'hero.jpg', 'hero.png', 'hero.jpeg', 'hero.webp'}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
        /* Clean, Readable Retro Monospace Typography */
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

        :root {{
            --bg-color: #050508;          /* Deep obsidian background */
            --card-bg: #0e0e14;          /* Soft dark container background */
            --text-color: #e6e6e6;        /* Clean off-white text for easy reading */
            --heading-color: #ffffff;     /* Pure white headings */
            --accent-color: #99ccff;      /* Soft blue accent for links */
            --hover-color: #ffffff;       /* Pure white hover highlight */
            --border-color: #222233;      /* Subtle dark border frame */
            --muted-text: #9090a0;       /* Muted gray text for captions */
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Space Mono', 'Courier Prime', 'Courier New', monospace;
            font-size: 1.05rem;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 2rem 1.5rem;
            max-width: 900px;
            margin: 0 auto;
        }}

        /* Breadcrumb Navigation Line */
        nav.breadcrumbs {{
            font-size: 0.95rem;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 0.6rem 1rem;
            margin-bottom: 2rem;
            color: var(--muted-text);
        }}

        nav.breadcrumbs a {{
            color: var(--accent-color);
            text-decoration: underline;
        }}

        nav.breadcrumbs a:hover {{
            color: var(--hover-color);
        }}

        /* Header & Hero Banner */
        header.page-header {{
            text-align: center;
            border: 1px solid var(--border-color);
            background: var(--card-bg);
            padding: 1.5rem;
            margin-bottom: 2.5rem;
        }}

        .hero-banner {{
            width: 100%;
            max-height: 420px;
            object-fit: cover;
            border: 1px solid var(--border-color);
            margin-bottom: 1.25rem;
        }}

        header.page-header h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--heading-color);
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }}

        /* Text Content Box */
        .text-content {{
            background: #000000;
            border: 1px solid var(--border-color);
            padding: 1.25rem;
            font-size: 1rem;
            color: var(--text-color);
            text-align: left;
            white-space: pre-wrap;
            margin-top: 1rem;
        }}

        section {{
            margin-bottom: 2.5rem;
        }}

        /* Subfolder Navigation Grid */
        .folder-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 1rem;
        }}

        .folder-card {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.8rem 1rem;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            color: var(--accent-color);
            text-decoration: none;
            font-size: 1rem;
            transition: border-color 0.2s ease, color 0.2s ease;
        }}

        .folder-card:hover {{
            border-color: var(--accent-color);
            color: var(--hover-color);
        }}

        /* Photos Section (Inline Embedded Files) */
        .image-gallery {{
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}

        .image-embed-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 0.8rem;
        }}

        .image-embed-card img {{
            width: 100%;
            height: auto;
            display: block;
            border: 1px solid var(--border-color);
        }}

        .image-embed-card .caption {{
            margin-top: 0.6rem;
            font-size: 0.9rem;
            color: var(--muted-text);
            text-align: center;
        }}

        /* Video & Audio Sections */
        .video-list, .audio-list {{
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}

        .video-card, .audio-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 1rem;
        }}

        .video-card video, .audio-card audio {{
            width: 100%;
        }}

        .video-card p, .audio-card span {{
            margin-top: 0.5rem;
            color: var(--text-color);
            font-size: 0.95rem;
        }}
    </style>
</head>
<body>
    <nav class="breadcrumbs">{breadcrumbs}</nav>

    <header class="page-header">
        {hero_html}
        <h1>{title}</h1>
        {text_section}
    </header>

    {subfolders_section}
    {images_section}
    {videos_section}
    {audios_section}
</body>
</html>
"""

def generate_breadcrumbs(root_dir: Path, current_dir: Path) -> str:
    rel_path = current_dir.relative_to(root_dir)
    parts = rel_path.parts
    
    parent_prefix = "../" * len(parts) if len(parts) > 0 else "./"
    home_url = parent_prefix + "index.html"
    crumbs = [f'<a href="{home_url}">Falcon in the Labyrinth</a>']
    
    for i, part in enumerate(parts):
        up_levels = len(parts) - 1 - i
        prefix = "../" * up_levels if up_levels > 0 else "./"
        url = prefix + "index.html"
        escaped_part = html.escape(part)
        if i == len(parts) - 1:
            crumbs.append(f"<span>{escaped_part}</span>")
        else:
            crumbs.append(f'<a href="{url}">{escaped_part}</a>')
            
    return " / ".join(crumbs)

def process_directory(root_dir: Path, current_dir: Path):
    entries = list(current_dir.iterdir())
    
    subfolders = []
    text_files = []
    image_files = []
    video_files = []
    audio_files = []
    hero_file = None
    
    for entry in entries:
        if entry.name.startswith('.'):
            continue
            
        if entry.is_dir():
            subfolders.append(entry)
        elif entry.is_file():
            ext = entry.suffix.lower()
            if entry.name.lower() in HERO_NAMES:
                hero_file = entry
            elif ext in TEXT_EXTS:
                text_files.append(entry)
            elif ext in IMAGE_EXTS:
                image_files.append(entry)
            elif ext in VIDEO_EXTS:
                video_files.append(entry)
            elif ext in AUDIO_EXTS:
                audio_files.append(entry)
                
    # Page Title
    folder_name = "Falcon in the Labyrinth" if current_dir == root_dir else current_dir.name
    
    # Hero Image HTML
    hero_html = ""
    if hero_file:
        encoded_hero = urllib.parse.quote(hero_file.name)
        escaped_folder = html.escape(folder_name)
        hero_html = f'<img src="./{encoded_hero}" alt="{escaped_folder}" class="hero-banner">'

    # Text Section
    text_html = ""
    if text_files:
        try:
            with open(text_files[0], 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    text_html = f'<div class="text-content">{html.escape(content)}</div>'
        except Exception as e:
            print(f"Error reading {text_files[0]}: {e}")

    # Subfolders Section (Without Title Classifier)
    subfolders_html = ""
    if subfolders:
        subfolders.sort(key=lambda x: x.name)
        items = []
        for sf in subfolders:
            encoded_name = urllib.parse.quote(sf.name)
            escaped_name = html.escape(sf.name)
            items.append(f'<a class="folder-card" href="./{encoded_name}/index.html">📁 <span>{escaped_name}</span></a>')
        joined_items = "\n".join(items)
        subfolders_html = f'<section>\n  <div class="folder-grid">\n{joined_items}\n  </div>\n</section>'

    # Photos Section (Inline Embedded Files Without Title Classifier)
    images_html = ""
    if image_files:
        image_files.sort(key=lambda x: x.name)
        items = []
        for img in image_files:
            encoded_name = urllib.parse.quote(img.name)
            escaped_stem = html.escape(img.stem)
            escaped_name = html.escape(img.name)
            items.append(f'<div class="image-embed-card">\n  <img src="./{encoded_name}" alt="{escaped_stem}" loading="lazy">\n  <div class="caption">{escaped_name}</div>\n</div>')
        joined_items = "\n".join(items)
        images_html = f'<section>\n  <div class="image-gallery">\n{joined_items}\n  </div>\n</section>'

    # Videos Section (Without Title Classifier)
    videos_html = ""
    if video_files:
        video_files.sort(key=lambda x: x.name)
        items = []
        for vid in video_files:
            encoded_name = urllib.parse.quote(vid.name)
            escaped_name = html.escape(vid.name)
            items.append(f'<div class="video-card">\n  <video controls preload="metadata">\n    <source src="./{encoded_name}">\n    Your browser does not support playing this video.\n  </video>\n  <p>{escaped_name}</p>\n</div>')
        joined_items = "\n".join(items)
        videos_html = f'<section>\n  <div class="video-list">\n{joined_items}\n  </div>\n</section>'

    # Audio Section (Without Title Classifier)
    audios_html = ""
    if audio_files:
        audio_files.sort(key=lambda x: x.name)
        items = []
        for aud in audio_files:
            encoded_name = urllib.parse.quote(aud.name)
            escaped_name = html.escape(aud.name)
            items.append(f'<div class="audio-card">\n  <span>🎵 {escaped_name}</span>\n  <audio controls preload="metadata" src="./{encoded_name}"></audio>\n</div>')
        joined_items = "\n".join(items)
        audios_html = f'<section>\n  <div class="audio-list">\n{joined_items}\n  </div>\n</section>'

    # Generate Breadcrumb navigation
    breadcrumbs = generate_breadcrumbs(root_dir, current_dir)

    # Render HTML page
    output_html = HTML_TEMPLATE.format(
        page_title=html.escape(folder_name),
        breadcrumbs=breadcrumbs,
        hero_html=hero_html,
        title=html.escape(folder_name),
        text_section=text_html,
        subfolders_section=subfolders_html,
        images_section=images_html,
        videos_section=videos_html,
        audios_section=audios_html
    )

    # Write index.html in the current folder
    index_file = current_dir / "index.html"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(output_html)

    print(f"Generated: {index_file}")

    # Recursively process subfolders
    for sf in subfolders:
        process_directory(root_dir, sf)

def main():
    import sys
    target_dir_str = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = Path(target_dir_str).resolve()
    
    print(f"Building Falcon in the Labyrinth static site at: {target_dir}")
    process_directory(target_dir, target_dir)
    print("Done! Open 'index.html' in your browser.")

if __name__ == "__main__":
    main()