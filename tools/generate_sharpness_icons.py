"""Regenerate Sharpness's original vector and platform icons (Pillow required)."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1] / 'program_info'
APP = 'io.github.Chekpoinss.SharpnessLauncher'
SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
<rect x="8" y="8" width="240" height="240" rx="56" fill="#141c2e"/>
<path d="M159 39 62 137h58l-23 80 97-111h-62z" fill="#7be8c3"/>
<path d="m159 39-27 67h62l-74 31 39-98z" fill="#c5fff0"/>
</svg>'''
(ROOT / f'{APP}.svg').write_text(SVG, encoding='utf-8')
image = Image.new('RGBA', (1024, 1024))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((32, 32, 992, 992), 224, fill='#141c2e')
draw.polygon([(636, 156), (248, 548), (480, 548), (388, 868), (776, 424), (528, 424)], fill='#7be8c3')
draw.polygon([(636, 156), (528, 424), (776, 424), (480, 548)], fill='#c5fff0')
image.resize((256, 256), Image.Resampling.LANCZOS).save(ROOT / f'{APP}_256.png')
image.save(ROOT / 'sharpnesslauncher.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
image.save(ROOT / 'sharpnesslauncher.icns')
