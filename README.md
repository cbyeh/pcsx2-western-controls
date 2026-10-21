# PCSX2 Western Controls

PCSX2 patches that switch three Japanese PS2 releases to the western button layout: **× confirms, ○ cancels**. On-screen button prompts are swapped to match, and a few optional extras are included.

| Game | Serial / CRC | Controls | Prompts | Extras |
|---|---|---|---|---|
| Kingdom Hearts Final Mix (English patch) | `SLPS-25198` / `BD3FB233` | ✅ patch | ✅ texture pack | Right-stick camera (normal or inverted), 16:9 widescreen, 60 FPS, HP/MP gauge fix |
| Kingdom Hearts II Final Mix+ (Crazycatz00 English patch) | `SLPM-66675` / `FAF99301` | ✅ patch | ✅ patch + texture pack | Works with PCSX2's built-in widescreen / 60 FPS / blackbar patches |
| Final Fantasy X International | `SLPS-25088` / `658597E2` | ✅ patch | ✅ patch | Works with PCSX2's built-in widescreen patch |

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
   - `Swap X and O button prompts`: FFX and KH2
   - KH1 only: `Right Stick Camera` **or** `Right Stick Camera (Inverted)` (pick one), `Widescreen 16:9`, `60 FPS`, optional `HP/MP gauge fix`
2. **Enable texture replacements** (needed for the KH1 prompts and KH2 menu icons). Settings → Graphics → **Texture Replacement**:
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

### Swap X and O button prompts (FFX, KH2)
- FFX: edits the button-icon sprite table (`0x3231A8`) so the ○ and × entries point at each other's artwork. This covers dialogue, tutorials, menus and Overdrive command lists.
- KH2: edits the button sprite table at `0x1D1FA60`, swapping both the symbol and the colour of the ○ and × entries, so tutorial boxes show a red ○. It only writes while that table is loaded. Menu icons come from the texture pack.

### Right Stick Camera (KH1)
KH1 on PS2 only rotates the camera with L2/R2. This patch turns right-stick left/right into L2/R2 for KH1's own camera rotation, **only while the game is in field mode** (KH1's main-loop mode `0x2BBDE0` = 3). In Gummi mode (5: world map, Gummi Garage, Gummi flight) it does nothing. So the Garage (L2 = build cursor down a layer, R2 = Inspect Mode) and flight (R2 = score display) never see fake presses. Deadzone: about half the stick travel.
- **Right Stick Camera**: push right → the camera swings right.
- **Right Stick Camera (Inverted)**: the opposite.
- Enable only one. Both write the same code, and the audit marks them as mutually exclusive.

### Widescreen 16:9 (KH1)
PCSX2 has no patches for this KH1 English-patch build, so this is a port of the database widescreen patch for `BD3FB870`. Every target was checked against this executable, and one bug was fixed: the original's "hor value second half" line writes `0x110898`, which is a stack store (`swc1 $f30`). The FOV constant's low half is actually at `0x110B34`.

### 60 FPS (KH1)
PeterDelta's 60 FPS patch from PCSX2's database (`BD3FB870`), ported unchanged; every address was checked against this build. It runs gameplay at 60 FPS with game speed compensated, and drops back to 30 FPS for FMVs and some scripted scenes. You may need EE Overclock (130%) for it to stay at 60.

### HP/MP gauge fix (KH1, optional)
From PCSX2's database (`BD3FB870`): nudges a few HP/MP gauge sprite rectangles by a pixel so the pieces line up. Every target holds the matching original value in this build. It doesn't change bar lengths: in KH1 the HP bar grows with max HP and the MP bar with max MP, so at high levels the HP bar is naturally longer.

### Digital pad mode
The DualShock 2 has an analog mode (ANALOG light on, sticks active) and a digital mode (light off: buttons and D-pad only). These games switch the pad to analog themselves, so you will normally only see digital mode if your PCSX2 controller is set to digital.
- **X/O swap:** works in both modes. In digital mode the pressure bytes it also swaps are unused, and they sit inside the game's own pad buffer.
- **Right Stick Camera:** analog mode only. It runs inside KH1's analog-mode branch, so in digital mode it does nothing.

## Testing

Tested in PCSX2 v2.9.129 with everything enabled at once:

- **KH1:** × confirms and ○ cancels in menus; ○ jumps and × doesn't. "Press ○ to jump" displays correctly. Right stick rotates the camera in both variants, and does nothing while paused. With a 100% save: the stick does nothing in the Gummi Garage (real R2 still switches to Inspect Mode) or in Gummi flight. The world map's button bar reads "× Depart". Widescreen renders correctly. With 60 FPS, the game reports 60 in the field; walking the same time at 60 and at 30 covers the same distance, and jumping works.
- **KH2:** × confirms (title, memory-card dialog, new-game menus); ○ cancels; ○ jumps with Widescreen + 60 FPS + Remove Blackbars enabled. The field tutorial shows "Jump with ○" with a red ○.
- **FFX:** × confirms and ○ cancels. Auron's Dragon Fang tutorial shows `↓←↑→ L1 R1 ○ ×`, and entering exactly that succeeded. Works with widescreen.
- **Conflicts:** [`tools/audit_pnach.py`](tools/audit_pnach.py) checks every patch section against every other one, including PCSX2's bundled `patches.zip`. Result: **0 overlapping writes** (the two camera variants overlap by design). The code caves (`0x000FD050–0x000FD22F`) were confirmed unused by all three games in live memory snapshots.

```
python tools/audit_pnach.py patches "<PCSX2 install>/resources/patches.zip"
```

## Known issues

- Prompt swaps for KH1/KH2 depend on texture replacement settings (see Install, step 2).

## Tools

- `tools/audit_pnach.py`: overlap/conflict checker for `.pnach` files (CI runs it on every push).
- `tools/chd_extract.py`: pulls `SYSTEM.CNF` and the boot ELF out of a PS2 DVD `.chd` (needs a `libchdr` shared library next to it). It's how these patches were verified against the actual executables.

## Credits

- KH1/KH2 X/O swap code: from the [PCSX2 patches database](https://github.com/PCSX2/pcsx2_patches) (sibling CRCs), ported and verified here.
- KH1 widescreen: Michael P / E.Mecenate (PCSX2 patches database), ported and fixed here.
- KH1 60 FPS: PeterDelta (PCSX2 patches database), ported here.
- FFX swap and prompts, KH2 prompts, KH1 camera, KH texture swaps, audit tool: this repo.

Texture replacements are edited copies of in-game icon sheets © Square Enix / Disney, included only so the prompts match the remapped controls. Code and patches: MIT (see `LICENSE`).
