"""
Named, machine-independent "Font & Alignment" profiles.

A profile is the Font & Alignment tab's values saved under a name, so the
same typeface setup (font file, size, alignment nudges, caret drop, draft
angle, ...) can be recalled later and - the actual point - carried ACROSS
machines: dial a font in on Blickensderfer, then apply the same profile to
Hammond or a Selectric without re-typing it.

Kept out of tune.py for the same reason lib/layouts/ and lib/system_fonts.py
are: this is data plumbing, not TUI code, and it stays free of third-party
imports beyond PyYAML so anything can read a profile without dragging in
textual.

Storage: config/profiles/font_and_alignment/<slug>.yaml, one file per
profile. The directory is created on first save. Each file is:

    name: Royal Vogue, Blickensderfer
    saved_from: blickensderfer      # informational only - never restricts
                                    # which machines can apply it
    values:
      font.path: "/home/.../Royal Vogue v3.ttf"
      font.size_mm: 3.7
      alignment.mode: center
      ...

`values` keys are dotted config paths ("font.size_mm"), NOT tune.py field
keys, deliberately: field keys are per-machine table entries that can be
renamed, while the config path is the thing actually being set and is
already what the FIELDS tables target. That also makes a profile file
readable and hand-editable without knowing anything about tune.py.

Cross-machine application is intentionally partial and lossless-by-
omission (see apply_to()):
  - a path the target machine HAS  -> applied
  - a path it does NOT have        -> skipped, reported, nothing invented
  - a path the target has but the profile lacks -> left untouched
Nothing is coerced or guessed. A Selectric has no `alignment.
center_offset_mm` and a Blickensderfer has no `alignment.x_pos_offset`;
each simply ignores the other's, while the genuinely shared core (font
path, mode, caret drop, underscore lift, draft angle, and font size for
everything except the Composer, which sizes by cap height) transfers.
"""

import os
import re

import yaml

PROFILE_DIRNAME = os.path.join("profiles", "font_and_alignment")


def profiles_dir(config_dir):
    """<config_dir>/profiles/font_and_alignment - the one place profiles
    live. Not created here; save_profile() makes it on demand."""
    return os.path.join(config_dir, PROFILE_DIRNAME)


def slugify(name):
    """Filename form of a profile name. Profiles are named for humans
    ("Royal Vogue, Blickensderfer"), so the display name is stored INSIDE
    the file and the filename is just a safe, stable derivative - the
    same split lib/layouts/ uses between a preset's display name and its
    dict key."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "profile"


def list_profiles(config_dir):
    """[(display_name, path), ...] sorted by display name, case-insensitive.
    Silently skips unreadable/malformed files rather than breaking the
    picker for every profile because one is bad."""
    d = profiles_dir(config_dir)
    if not os.path.isdir(d):
        return []
    out = []
    for fn in os.listdir(d):
        if not fn.endswith((".yaml", ".yml")):
            continue
        path = os.path.join(d, fn)
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            name = data.get("name") or os.path.splitext(fn)[0]
            if isinstance(data.get("values"), dict):
                out.append((str(name), path))
        except Exception:
            continue
    out.sort(key=lambda nv: nv[0].lower())
    return out


def load_profile(path):
    """(display_name, {dotted_path: value}). Raises on a malformed file -
    unlike list_profiles(), a profile the user explicitly picked failing
    to load should be loud, not silently skipped."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    values = data.get("values")
    if not isinstance(values, dict):
        raise ValueError(f"{path}: no 'values' mapping - not a profile file")
    return str(data.get("name") or os.path.splitext(os.path.basename(path))[0]), values


def save_profile(config_dir, name, values, saved_from=None):
    """Writes a profile and returns its path. Overwrites an existing
    profile of the same slug on purpose: re-saving under a name you
    already used is an update, which is what "Save" means when the name
    is already in the picker."""
    d = profiles_dir(config_dir)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, slugify(name) + ".yaml")
    doc = {"name": name, "values": {k: values[k] for k in sorted(values)}}
    if saved_from:
        doc["saved_from"] = saved_from
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Font & Alignment profile - see lib/font_profiles.py.\n"
                "# 'values' keys are dotted config paths; a machine without a\n"
                "# given path simply skips it when this profile is applied.\n")
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return path


# ---------------------------------------------------------------- Equivalences
# Config paths that are the SAME KNOB spelled differently by different
# machine families, so a profile carrying one can still set the other.
# Each group maps path -> direction factor; transferring between two paths
# multiplies by (target_factor / source_factor). Factors apply to numeric
# values only - a character-set string is copied as-is.
#
# Directions were measured, not assumed, by pushing a glyph through each
# family's real transform stack and reading off d(mean x)/d(offset):
#
#   modified_left_offset_mm (cylinder) -> -1.0    | agree, factor +1
#   custom_h_offset         (spherical) -> -1.0   |
#
#   center_offset_mm        (cylinder) -> -1.0    | OPPOSE, factor -1
#   x_pos_offset            (spherical) -> +1.0   |
#
# The per-character pair agreeing is not luck: the cylinder family applies
# its offset BEFORE mirror([1,0,0]) and the spherical family applies its
# AFTER, with v2/ibm.scad:501 writing `X_Pos_Offset - customhalign` - the
# two negations cancel. The GLOBAL pair opposes because X_Pos_Offset is
# added after the mirror with a plus. (v2 is itself inconsistent here:
# ibm.scad:1034's test-string path uses `+customhalign`, because that path
# is not mirrored.)
#
# Deliberately NOT equated:
#   font2.font2_composer_cap_height - the Composer sizes by CAP HEIGHT,
#     not mm (Font_Size_Selected = cap_height/2.834), so equating it with
#     a mm size would be a unit error, not a rename.
#   alignment.custom_v_chars/custom_v_offset - a generic per-character
#     VERTICAL group with no cylinder counterpart; caret_drop_mm/
#     underscore_lift_mm are two fixed-character specialisations of the
#     same idea, not the same knob.
#   alignment.modified_right_* - the spherical family has only one
#     per-character horizontal group, so there is nothing to pair it with.
EQUIVALENT_PATHS = [
    {"alignment.modified_left_chars": 1.0, "alignment.custom_h_chars": 1.0},
    {"alignment.modified_left_offset_mm": 1.0, "alignment.custom_h_offset": 1.0},
    {"alignment.center_offset_mm": 1.0, "alignment.x_pos_offset": -1.0},
    {"char_mod.char": 1.0, "font2.font2_chars": 1.0},
    {"char_mod.char_mod_font_path": 1.0, "font2.font2_path": 1.0},
    {"char_mod.char_mod_size_mm": 1.0, "font2.font2_size_mm": 1.0},
]


def _equivalents(path):
    """{other_path: factor_to_convert_INTO_it} for one path."""
    for group in EQUIVALENT_PATHS:
        if path in group:
            src = group[path]
            return {k: v / src for k, v in group.items() if k != path}
    return {}


def translate(path, value, target_paths):
    """(target_path, converted_value) if `path` can reach one of
    target_paths via an equivalence, else None. Numeric values are scaled
    by the direction factor; strings are copied unchanged."""
    for other, factor in _equivalents(path).items():
        if other in target_paths:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return other, value
            # `+ 0.0` normalises -0.0 (from negating a zero) back to 0.0 -
            # numerically identical, but -0.0 in a config file reads as a bug.
            return other, value * factor + 0.0
    return None


def get_nested(cfg, path):
    d = cfg
    for k in path:
        d = d[k]
    return d


def collect_from_config(cfg, field_paths):
    """{dotted_path: value} for every field path the config actually has.
    field_paths is the list of ["section", "key"] lists from a machine's
    Font & Alignment FIELDS table."""
    out = {}
    for path in field_paths:
        try:
            out[".".join(path)] = get_nested(cfg, path)
        except (KeyError, TypeError):
            continue
    return out


def apply_to(profile_values, field_paths):
    """Splits a profile against one machine's Font & Alignment field
    paths, without touching any config - the caller decides what to do
    with the result.

    Returns (applied, aliased, skipped, unset):
      applied - {path: value} the machine has and the profile sets directly
      aliased - {path: (value, source_path)} reached through
                EQUIVALENT_PATHS, i.e. the same knob under this family's
                own name, direction-corrected
      skipped - profile paths with no field and no equivalent here
      unset   - paths the machine has that nothing in the profile reaches,
                which therefore keep their current value

    `unset` is the one worth surfacing to a user: it is where a profile
    from a different machine family leaves real knobs at whatever they
    happened to be, which is usually harmless but is the only case that
    can quietly need a look."""
    have = {".".join(p) for p in field_paths}
    applied, aliased, skipped = {}, {}, []
    for k, v in profile_values.items():
        if k in have:
            applied[k] = v
            continue
        moved = translate(k, v, have)
        if moved is not None:
            aliased[moved[0]] = (moved[1], k)
        else:
            skipped.append(k)
    covered = set(applied) | set(aliased)
    return applied, aliased, sorted(skipped), sorted(have - covered)


def matching_profile(config_dir, cfg, field_paths):
    """Display name of the profile whose values all match this config, or
    None. Derived by comparison rather than stored in the config, exactly
    like tune.py's _current_layout_preset() derives the active layout from
    the rows themselves - so hand-editing a value correctly drops the
    selection instead of leaving a stale name pointing at something that
    is no longer true.

    Only the paths the profile actually carries are compared: a profile
    saved on another machine legitimately says nothing about this
    machine's extra fields, and should still read as "active" when
    everything it does specify matches."""
    current = collect_from_config(cfg, field_paths)
    for name, path in list_profiles(config_dir):
        try:
            _, values = load_profile(path)
        except Exception:
            continue
        shared = {k: v for k, v in values.items() if k in current}
        if shared and all(current[k] == v for k, v in shared.items()):
            return name
    return None
