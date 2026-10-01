# Realistic Mario – Level 1-1 Inspired

A short Pygame prototype of a **realistic** take on classic Mario platforming.

Mario can actually die from head trauma when he hits bricks from below, and he drowns in water if he stays under too long. Uses the excellent [Realistic Mario – Basic Sprites](https://mfgg.net/index.php?act=resdb&param=02&c=1&id=34896) sheet by John_Santos (inspired by the old Pete Holmes “Realistic Mario” videos).

> This is an **original level** loosely inspired by the spirit of Super Mario Bros. 1-1.  
> It is **not** a recreation or redistribution of Nintendo’s copyrighted level data, graphics, or music.

## Features

- Headbonk death on brick blocks (realistic trauma)
- Oxygen meter + drowning in water sections
- Simple but satisfying platforming
- Auto-downloads the sprite sheet from MFGG on first run
- Clean, single-file codebase that’s easy to expand

## Quick Start

```bash
pip install -r requirements.txt
python realistic_mario_1_1.py
```

**Controls**
- Arrow keys / WASD – move
- Space / W / Up – jump
- R – restart after death
- Esc – quit

## Credits

- Sprite sheet: **John_Santos** – “Realistic Mario – Basic Sprites” on [Mario Fan Games Galaxy](https://mfgg.net)
- Concept inspiration: Pete Holmes’ Realistic Mario animation series
- Code: restii-dev + Grok

## License

Code is MIT.  
Sprite sheet remains under whatever license John_Santos published it under on MFGG (credit required).  
Nintendo owns Super Mario. This is a fan prototype only.
