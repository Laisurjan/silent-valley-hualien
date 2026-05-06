"""Generate project images with OpenAI gpt-image-2.

Setup:
  pip install openai
  set OPENAI_API_KEY=sk-...

Usage examples:
  python scripts/generate_images.py --list
  python scripts/generate_images.py --dry-run
  python scripts/generate_images.py --only hero_valley
  python scripts/generate_images.py --force
  python scripts/generate_images.py --clean-mock
"""

from pathlib import Path
import argparse
import base64
from datetime import datetime
import json
import os
import time


OUTPUT_DIR = Path("C:/culturereports/assets/images")
LOG_FILE = OUTPUT_DIR / "GENERATION_LOG.md"

PRICING = {
    "1792x1024": 0.08,
    "1024x1024": 0.04,
    "1024x512": 0.02,
}

HARD_CONSTRAINTS = """HARD CONSTRAINTS (must follow):
- ABSOLUTELY NO people, no human figures, no silhouettes, no shadows of humans
- NO traditional indigenous clothing, face tattoos, ceremonial objects, or tribal patterns
- NO buildings with cultural/ceremonial significance
- NO ceremonial plants as subjects (millet, ramie, betel nut)
- ONLY pure landscape and nature elements
- Abundant white space (negative space) for text overlay
- Soft ink wash gradients, minimal pigment, suggestive rather than detailed
- Style: Song dynasty literati painting (sumi-e influence)
- Restrained palette: indigo, ochre, ink black on paper texture
- Quiet contemplative mood"""

IMAGES = [
    {
        "filename": "hero_valley.png",
        "size": "1792x1024",
        "title": "花蓮縱谷俯瞰",
        "description": "Aerial view of Hualien longitudinal valley in eastern Taiwan, Central Mountain Range and Coastal Mountain Range flanking wide alluvial valley, Xiuguluan River meandering, soft morning mist over rice paddies, dawn light, no modern development",
    },
    {
        "filename": "event_cepo.png",
        "size": "1024x1024",
        "title": "大港口 Cepo 秀姑巒溪出海口",
        "description": "Mouth of Xiuguluan River entering Pacific Ocean on east coast, dark basalt sea stacks, ocean waves, scattered offshore reefs, salt mist, no boats or piers",
    },
    {
        "filename": "event_dafen.png",
        "size": "1024x1024",
        "title": "大分玉山國家公園深山",
        "description": "Deep mountain wilderness of Yushan National Park, layered mountain peaks fading into clouds, primeval cedar and hemlock forest suggested by ink dabs, no buildings, no settlements",
    },
    {
        "filename": "event_cikasuan.png",
        "size": "1024x1024",
        "title": "七腳川吉安鄉縱谷田疇",
        "description": "Rice paddy fields in longitudinal valley plain of Jian Township Hualien, foothills in distance, irrigation channels, willow trees by ink strokes, no people, no farm buildings",
    },
    {
        "filename": "event_truku.png",
        "size": "1024x1024",
        "title": "太魯閣立霧溪峽谷",
        "description": "Taroko Gorge by Liwu River cutting through marble cliffs, towering vertical white-grey marble walls, river far below, mist rising, no roads no tunnels no infrastructure",
    },
    {
        "filename": "divider_mountain.png",
        "size": "1024x512",
        "title": "中央山脈遠山輪廓淡影",
        "description": "Distant silhouette of layered mountain ranges in faint ink wash, three to four overlapping ridges, abundant white sky, horizontal banner, very minimal",
    },
    {
        "filename": "divider_water.png",
        "size": "1024x512",
        "title": "水流線條淡墨",
        "description": "Flowing water in ink wash strokes suggesting river current, horizontal banner, abundant white space, curved ink lines, no shore no landscape pure abstraction",
    },
    {
        "filename": "divider_coast.png",
        "size": "1024x512",
        "title": "太平洋海岸線淡墨",
        "description": "Pacific Ocean coastline as faint horizontal ink wash band, distant horizon, few sea-stack rocks, abundant white sky, horizontal banner",
    },
    {
        "filename": "divider_valley.png",
        "size": "1024x512",
        "title": "縱谷剖面淡墨",
        "description": "Cross-section silhouette of Hualien longitudinal valley, Central Mountain Range left, Coastal Mountain Range right, valley floor, faint ink wash, abundant white sky, horizontal banner",
    },
]


MOCK_FILES = [item["filename"] for item in IMAGES]


def build_prompt(item):
    return f"{item['title']}\n\n{item['description']}\n\n{HARD_CONSTRAINTS}"


def image_path(item):
    return OUTPUT_DIR / item["filename"]


def cost_for(item):
    return PRICING[item["size"]]


def filtered_images(only):
    if not only:
        return IMAGES
    matches = [item for item in IMAGES if Path(item["filename"]).stem == only]
    if not matches:
        valid = ", ".join(Path(item["filename"]).stem for item in IMAGES)
        raise SystemExit(f"ERROR: No image matches --only {only!r}. Valid names: {valid}")
    return matches


def print_image_list(items):
    print("Images:")
    for item in items:
        status = "exists" if image_path(item).exists() else "missing"
        print(f"- {item['filename']:<21} {item['size']:<9} {status}")
    print(f"Total listed: {len(items)}")


def print_dry_run(items):
    print("Dry run: no API call will be made.")
    total = 0.0
    for item in items:
        cost = cost_for(item)
        total += cost
        print()
        print(f"Filename: {item['filename']}")
        print(f"Size: {item['size']}")
        print(f"Estimated cost: {cost:.2f} USD")
        print("Prompt:")
        print(build_prompt(item))
    print_summary(items, total, dry_run=True)


def clean_mock_files():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename in MOCK_FILES:
        target = OUTPUT_DIR / filename
        if target.exists():
            target.unlink()
            print(f"Deleted mock file: {target}")


def require_api_key():
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "ERROR: OPENAI_API_KEY is not set.\n"
            "Run this from Windows cmd first:\n"
            "  set OPENAI_API_KEY=sk-..."
        )


def selected_model(client):
    models = client.models.list()
    ids = []
    for model in models.data:
        model_id = getattr(model, "id", "")
        if model_id.startswith("gpt-image-") and model_id != "gpt-image-1":
            ids.append(model_id)
    if "gpt-image-2" in ids:
        return "gpt-image-2"
    if ids:
        return sorted(ids)[-1]
    raise SystemExit("ERROR: No allowed gpt-image-* model found. Refusing fallback to dall-e-* or gpt-image-1.")


def is_transient_error(error):
    status_code = getattr(error, "status_code", None)
    if status_code in (408, 409, 429, 500, 502, 503, 504):
        return True
    name = error.__class__.__name__.lower()
    text = str(error).lower()
    markers = ("rate", "timeout", "temporar", "connection", "server", "service unavailable")
    return any(marker in name or marker in text for marker in markers)


def generate_with_retry(client, model, item):
    delays = [2, 4, 8]
    last_error = None
    for attempt in range(1, 5):
        try:
            return client.images.generate(
                model=model,
                prompt=build_prompt(item),
                size=item["size"],
                n=1,
            )
        except Exception as error:
            last_error = error
            if attempt == 4 or not is_transient_error(error):
                raise
            delay = delays[attempt - 1]
            print(f"Transient error for {item['filename']} on attempt {attempt}: {error}")
            print(f"Retrying in {delay}s...")
            time.sleep(delay)
    raise last_error


def response_to_png_bytes(response):
    data = getattr(response, "data", None)
    if not data:
        raise ValueError("Image response did not contain data.")
    first = data[0]
    b64_json = getattr(first, "b64_json", None)
    if b64_json:
        return base64.b64decode(b64_json)
    url = getattr(first, "url", None)
    if url:
        from urllib.request import urlopen

        with urlopen(url, timeout=120) as handle:
            return handle.read()
    raise ValueError("Image response contained neither b64_json nor url.")


def write_generation_log(results, failures, total):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    lines = [
        f"# Image Generation Log - {timestamp}",
        "",
        "| Filename | Size | Status | Cost | Detail |",
        "|---|---:|---|---:|---|",
    ]
    for result in results:
        lines.append(
            f"| {result['filename']} | {result['size']} | {result['status']} | "
            f"{result['cost']:.2f} USD | {result['detail']} |"
        )
    for failure in failures:
        lines.append(
            f"| {failure['filename']} | {failure['size']} | failed | "
            f"{failure['cost']:.2f} USD | {failure['error']} |"
        )
    lines.extend(["", f"Grand total estimated cost: {total:.2f} USD", ""])
    LOG_FILE.write_text("\n".join(lines), encoding="utf-8")


def print_summary(items, total, dry_run=False):
    print()
    print("Summary:")
    print(f"{'Filename':<21} {'Size':<9} {'Cost':>8}")
    print("-" * 42)
    for item in items:
        print(f"{item['filename']:<21} {item['size']:<9} {cost_for(item):>5.2f} USD")
    label = "Grand total estimate" if dry_run else "Grand total"
    print("-" * 42)
    print(f"{label}: {total:.2f} USD")


def generate_images(items, force):
    require_api_key()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    from openai import OpenAI

    client = OpenAI()
    model = selected_model(client)
    print(f"Selected model: {model}")

    results = []
    failures = []
    total = 0.0

    for item in items:
        target = image_path(item)
        cost = cost_for(item)
        if target.exists() and not force:
            print(f"Skipping existing: {target}")
            results.append(
                {
                    "filename": item["filename"],
                    "size": item["size"],
                    "status": "skipped",
                    "cost": 0.0,
                    "detail": "already exists",
                }
            )
            continue
        try:
            print(f"Generating {item['filename']} ({item['size']})...")
            response = generate_with_retry(client, model, item)
            png_bytes = response_to_png_bytes(response)
            target.write_bytes(png_bytes)
            total += cost
            print(f"Saved: {target}")
            print(f"Cost: {cost:.2f} USD")
            results.append(
                {
                    "filename": item["filename"],
                    "size": item["size"],
                    "status": "generated",
                    "cost": cost,
                    "detail": f"model={model}",
                }
            )
        except Exception as error:
            print(f"FAILED {item['filename']}: {error}")
            failures.append(
                {
                    "filename": item["filename"],
                    "size": item["size"],
                    "cost": cost,
                    "error": str(error).replace("|", "/"),
                }
            )

    print_summary(items, total)
    write_generation_log(results, failures, total)
    print(f"Wrote log: {LOG_FILE}")
    if failures:
        print()
        print("Failures:")
        for failure in failures:
            print(f"- {failure['filename']}: {failure['error']}")
        raise SystemExit(2)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate 縱谷無言 landscape images with OpenAI gpt-image-* models.")
    parser.add_argument("--only", metavar="NAME", help="Generate only image matching filename stem.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files. Default skips existing files.")
    parser.add_argument("--list", action="store_true", help="Print 9 images with status and make no API call.")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts and cost estimates and make no API call.")
    parser.add_argument("--clean-mock", action="store_true", help="Delete the 9 exact mock PNG files before continuing.")
    return parser.parse_args()


def main():
    args = parse_args()
    items = filtered_images(args.only)

    if args.clean_mock:
        clean_mock_files()

    if args.list:
        print_image_list(items)
        return

    if args.dry_run:
        print_dry_run(items)
        return

    generate_images(items, args.force)


if __name__ == "__main__":
    main()
