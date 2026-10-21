# PCSX2 Western Controls

PCSX2 patches that switch three Japanese PS2 releases to the western button layout: **× confirms, ○ cancels**. On-screen button prompts are swapped to match, and a few optional extras are included.

| Game | Serial / CRC | Controls | Prompts | Extras |
|---|---|---|---|---|
| Kingdom Hearts Final Mix (English patch) | `SLPS-25198` / `BD3FB233` | ✅ patch | ✅ texture pack | Right-stick camera (normal or inverted), 16:9 widescreen |
| Kingdom Hearts II Final Mix+ (Crazycatz00 English patch) | `SLPM-66675` / `FAF99301` | ✅ patch | ✅ texture pack ¹ | Works with PCSX2's built-in widescreen / 60 FPS / blackbar patches |
| Final Fantasy X International | `SLPS-25088` / `658597E2` | ✅ patch | ✅ patch | Works with PCSX2's built-in widescreen patch |

¹ In KH2's in-field tutorial boxes the swapped ○ is drawn in ×'s blue tint, because the game colours each icon in code. Menus and pause screens show the correct red ○. See [Known issues](#known-issues).

The swap happens at the controller-read level, so it applies everywhere: menus, field, battle, minigames, and FFX Overdrive inputs. The FFX prompt patch also swaps the ○/× icons in Overdrive command lists. That makes the result match the US release, where Auron's Dragon Fang reads `↓ ← ↑ → L1 R1 ○ ×` (JP: `… × ○`).

## Check your version

These patches only load for an exact **serial + CRC** match. In PCSX2, right-click the game → **Properties → Summary** and compare the Serial and CRC with the table. Other dumps or other English-patch versions have different CRCs and won't load these files.

## Install

Download the release zip and copy its folders into your PCSX2 user folder (on Windows usually `Documents\PCSX2`):

```
PCSX2/
├── patches/
│   ├── SLPS-25198_BD3FB233_WesternControls.pnach
│   ├── SLPM-66675_FAF99301_WesternControls.pnach
│   └── SLPS-25088_658597E2_WesternControls.pnach
└── textures/
    ├── SLPS-25198/replacements/*.png
    └── SLPM-66675/replacements/*.png
```

Then, in PCSX2:

1. **Enable the patches.** Right-click the game → Properties → **Patches**, and tick what you want:
   - `Swap X and O (Western controls)`: all three games
   - `Swap X and O button prompts`: FFX
   - KH1 only: `Right Stick Camera` **or** `Right Stick Camera (Inverted)` (pick one), and `Widescreen 16:9`
2. **Enable texture replacements** (needed for the KH1/KH2 prompts). Settings → Graphics → **Texture Replacement**:
   - ✅ Load Textures
   - ☐ Asynchronous Texture Loading (turn **off**)
   - ✅ Precache Textures

   With async loading on, the original icons can stay on screen.
3. Restart the game. PCSX2 only re-reads patch files when a game boots, or when you click **Reload Patches** in the Patches tab.

## Patch details

### Swap X and O (Western controls)
Hooks the game's pad-read routine and swaps the Circle/Cross bits and their pressure bytes before the game sees them.
- KH1 / KH2: ported from PCSX2's database patches for the sibling English-patch CRCs (`BD3FB870`, `E6FB8E10`). The hook points were verified byte-identical in these builds.
- FFX: new. Hooks the end of libpad `scePadRead` (`0x2DDEB8`).

### Swap X and O button prompts (FFX)
Edits FFX's button-icon sprite table (`0x3231A8`) so the ○ and × entries point at each other's artwork. This covers dialogue, tutorials, menus and Overdrive command lists.

### Right Stick Camera (KH1)
KH1 on PS2 only rotates the camera with L2/R2. This patch turns right-stick left/right into L2/R2 while the pad is in analog mode, using KH1's own camera rotation. Deadzone: about half the stick travel.
- **Right Stick Camera**: push right → the camera swings right.
- **Right Stick Camera (Inverted)**: the opposite.
- Enable only one. Both write the same code, and the audit marks them as mutually exclusive.

### Widescreen 16:9 (KH1)
PCSX2 has no patches for this KH1 English-patch build, so this is a port of the database widescreen patch for `BD3FB870`. Every target was checked against this executable, and one bug was fixed: the original's "hor value second half" line writes `0x110898`, which is a stack store (`swc1 $f30`). The FOV constant's low half is actually at `0x110B34`.

## Testing

Tested in PCSX2 v2.9.129 with everything enabled at once:

- **KH1:** × confirms and ○ cancels in menus; ○ jumps and × doesn't. "Press ○ to jump" displays correctly. Right stick rotates the camera in both variants, and does nothing while paused. Widescreen renders correctly.
- **KH2:** × confirms (title, memory-card dialog, new-game menus); ○ cancels; ○ jumps with Widescreen + 60 FPS + Remove Blackbars enabled. Prompts show ○.
- **FFX:** × confirms and ○ cancels. Auron's Dragon Fang tutorial shows `↓←↑→ L1 R1 ○ ×`, and entering exactly that succeeded. Works with widescreen.
- **Conflicts:** [`tools/audit_pnach.py`](tools/audit_pnach.py) checks every patch section against every other one, including PCSX2's bundled `patches.zip`. Result: **0 overlapping writes** (the two camera variants overlap by design). The code caves (`0x000FD050–0x000FD22F`) were confirmed unused by all three games in live memory snapshots.

```
python tools/audit_pnach.py patches "<PCSX2 install>/resources/patches.zip"
```

## Known issues

- **KH2 in-field tutorial icons:** the ○ symbol appears with ×'s blue tint, because KH2 builds those icons from a grey symbol plus a per-button colour chosen in code. Pause and menu screens show the correct red ○. Fixing the tint means patching KH2's text renderer; contributions are welcome.
- **KH1 Gummi Ship (untested):** if the PS2 version uses L2/R2 there, the right stick will trigger them too. Disable the camera patch if this bothers you.
- Prompt swaps for KH1/KH2 depend on texture replacement settings (see Install, step 2).

## Tools

- `tools/audit_pnach.py`: overlap/conflict checker for `.pnach` files (CI runs it on every push).
- `tools/chd_extract.py`: pulls `SYSTEM.CNF` and the boot ELF out of a PS2 DVD `.chd` (needs a `libchdr` shared library next to it). It's how these patches were verified against the actual executables.

## Credits

- KH1/KH2 X/O swap code: from the [PCSX2 patches database](https://github.com/PCSX2/pcsx2_patches) (sibling CRCs), ported and verified here.
- KH1 widescreen: Michael P / E.Mecenate (PCSX2 patches database), ported and fixed here.
- FFX swap and prompts, KH1 camera, KH texture swaps, audit tool: this repo.

Texture replacements are edited copies of in-game icon sheets © Square Enix / Disney, included only so the prompts match the remapped controls. Code and patches: MIT (see `LICENSE`).
