---
name: image-video-prompts
description: Library of ~2,600 curated image and video generation prompts (Nano Banana, GPT Image, Midjourney, Seedance, Kling, Veo, etc.) with model, mode, category, tags and notes on why each works, plus ffmpeg video-editing recipes. Use when writing a prompt to generate or edit images or video — e.g. product hero shots, industrial/factory scenes, banners, social visuals or hero videos for the LICHTZEN site — or when the user asks for prompt ideas.
---

# Image and video prompt library

Source: https://github.com/ai-boost/awesome-image-video-prompts (GPL-3.0, see LICENSE). Preview images are not included.

## How to use

1. Search `index.tsv` (columns: path, mode, category, model, title, tags) with Grep — e.g. `product`, `industrial`, `studio`, `macro`, `video`, a model name.
2. Open 2–5 matching YAML files under `prompts/image/` or `prompts/video/`. Each has `prompt`, `notes` (why it works), `model`, `mode` and `source`.
3. Adapt the structure (subject, materials, lighting, lens, composition, mood) to the brief instead of copying a prompt verbatim. Keep brand facts accurate; do not invent products, certifications or people.
4. `recipes/` holds ffmpeg-based video editing recipes (split shots, subtitles, blur-fill vertical, teaser montage).
