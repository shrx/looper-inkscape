#!/usr/bin/env python3
# coding=utf-8
#
# Looper for Inkscape
#
# A port of the "Looper" Sketch plugin by Sures Kumar
#   https://github.com/sureskumar/Looper
# Original plugin (c) Sures Kumar, MIT license.
#
# Duplicates the selected object or group while progressively rotating,
# scaling, moving and fading the copies, to create geometric and organic
# patterns.

import copy as _pycopy
import math
import random

import inkex


# ---------------------------------------------------------------------------
# Minimal affine matrix helpers, using the SVG (a, b, c, d, e, f) convention:
#   x' = a*x + c*y + e
#   y' = b*x + d*y + f
# Kept self-contained so the extension works across inkex API versions.
# ---------------------------------------------------------------------------

def mat_mul(m1, m2):
    """Compose two matrices: apply m2 first, then m1."""
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def mat_translate(tx, ty):
    return (1.0, 0.0, 0.0, 1.0, tx, ty)


def mat_scale(sx, sy):
    return (sx, 0.0, 0.0, sy, 0.0, 0.0)


def mat_rotate_deg(angle, cx, cy):
    """Rotation by `angle` degrees around point (cx, cy)."""
    rad = math.radians(angle)
    cos, sin = math.cos(rad), math.sin(rad)
    rot = (cos, sin, -sin, cos, 0.0, 0.0)
    return mat_mul(mat_translate(cx, cy), mat_mul(rot, mat_translate(-cx, -cy)))


def mat_to_attr(m):
    return "matrix({:.8g},{:.8g},{:.8g},{:.8g},{:.8g},{:.8g})".format(*m)


IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
MIN_DIM = 1e-3  # keep width/height from collapsing to zero or flipping


class Looper(inkex.EffectExtension):
    """Duplicate the selection with incremental rotate/scale/move/opacity."""

    def add_arguments(self, pars):
        pars.add_argument("--tab", default="count")

        # Count
        pars.add_argument("--copies", type=int, default=5)
        pars.add_argument("--hide_original", type=inkex.Boolean, default=False)
        pars.add_argument("--seed", type=int, default=0)

        # Rotate
        pars.add_argument("--rotate_enable", type=inkex.Boolean, default=True)
        pars.add_argument("--rotate_mode", default="auto",
                          choices=["auto", "manual"])
        pars.add_argument("--angle", type=float, default=4.0)
        pars.add_argument("--rotate_inc", default="linear",
                          choices=["linear", "sin", "random"])
        pars.add_argument("--sin_factor", type=float, default=0.8)
        pars.add_argument("--angle_rnd", type=float, default=5.0)

        # Scale
        pars.add_argument("--scale_enable", type=inkex.Boolean, default=False)
        pars.add_argument("--scale_mode", default="pixels",
                          choices=["pixels", "percentage", "random"])
        pars.add_argument("--scale_dir", default="both",
                          choices=["both", "x", "y"])
        pars.add_argument("--scale_px", type=float, default=5.0)
        pars.add_argument("--scale_pr", type=float, default=102.0)
        pars.add_argument("--scale_rnd", type=float, default=5.0)

        # Move
        pars.add_argument("--move_enable", type=inkex.Boolean, default=False)
        pars.add_argument("--move_dir", default="horizontal",
                          choices=["horizontal", "vertical", "diagonal",
                                   "random"])
        pars.add_argument("--move_inc", type=float, default=20.0)
        pars.add_argument("--move_rnd_x", type=float, default=20.0)
        pars.add_argument("--move_rnd_y", type=float, default=20.0)

        # Grid
        pars.add_argument("--grid_enable", type=inkex.Boolean, default=False)
        pars.add_argument("--grid_cols", type=int, default=4)
        pars.add_argument("--grid_rows", type=int, default=4)
        pars.add_argument("--grid_margin_x", type=float, default=50.0)
        pars.add_argument("--grid_margin_y", type=float, default=50.0)

        # Opacity
        pars.add_argument("--opacity_mode", default="none",
                          choices=["none", "random", "fadein", "fadeout"])

    # ------------------------------------------------------------------

    def effect(self):
        opt = self.options

        selection = [node for node in self.svg.selection]
        if not selection:
            raise inkex.AbortExtension(
                "Select an object or group to duplicate. Cheers!")
        if len(selection) > 1:
            raise inkex.AbortExtension(
                "Select only one object or group to duplicate. Cheers!")
        node = selection[0]

        bbox = node.bounding_box()
        if bbox is None:
            raise inkex.AbortExtension(
                "Could not determine the bounding box of the selection.")

        rng = random.Random(opt.seed) if opt.seed else random.Random()

        # In the original panel, Move and Grid are mutually exclusive and
        # Move wins if both are somehow on.
        move_mode = opt.move_dir if opt.move_enable else None
        grid = opt.grid_enable and not opt.move_enable

        if grid:
            cols = max(opt.grid_cols, 1)
            rows = max(opt.grid_rows, 1)
            total = cols * rows
        else:
            cols = rows = 0
            total = max(opt.copies, 1)

        if opt.rotate_mode == "auto":
            angle = 360.0 / total
            angle_mode = "linear"
        else:
            angle = opt.angle
            angle_mode = opt.rotate_inc

        # Original (unrotated) frame in parent coordinates.
        ox, oy = bbox.left, bbox.top
        ow = bbox.width if bbox.width else MIN_DIM
        oh = bbox.height if bbox.height else MIN_DIM

        # Existing transform of the source node (already reflected in bbox).
        elem_mat = self.get_node_matrix(node)

        # Target group, inserted as a sibling right after the original.
        group = inkex.Group()
        label = node.label or node.get("id") or "looper"
        group.label = "{}_looper".format(label)
        node.addnext(group)

        # Mutable state: unrotated frame + accumulated rotation.
        x, y, w, h = ox, oy, ow, oh
        rot = 0.0
        sin_counter = 0.0
        grid_x0, grid_y0 = ox, oy
        grid_row_count = 0

        for i in range(1, total + 1):
            dup = self.make_copy(node)
            dup.label = "{}_{}".format(label, i)

            # Frame transform: map original frame -> current frame, then
            # rotate around the current frame's centre (like Sketch does).
            sx, sy = w / ow, h / oh
            frame_mat = mat_mul(
                mat_translate(x, y),
                mat_mul(mat_scale(sx, sy), mat_translate(-ox, -oy)))
            if rot:
                frame_mat = mat_mul(
                    mat_rotate_deg(rot, x + w / 2.0, y + h / 2.0), frame_mat)
            final_mat = mat_mul(frame_mat, elem_mat)
            if final_mat != IDENTITY:
                dup.set("transform", mat_to_attr(final_mat))
            elif dup.get("transform"):
                dup.attrib.pop("transform")

            opacity = self.opacity_for(i, total, rng)
            if opacity is not None:
                dup.style["opacity"] = "{:.4g}".format(opacity)

            group.append(dup)

            if i == total:
                break

            # ---- advance the state for the next copy (ported switch logic)

            # Rotate
            if opt.rotate_enable:
                if angle_mode == "linear":
                    cur_angle = angle
                elif angle_mode == "sin":
                    # Faithful to the original: the per-step increment is
                    # sin(counter) degrees; the factor drives the frequency.
                    cur_angle = math.sin(sin_counter)
                    sin_counter += math.pi * opt.sin_factor / 100.0
                else:  # random
                    cur_angle = rng.uniform(angle - opt.angle_rnd,
                                            angle + opt.angle_rnd)
                rot += cur_angle

            # Scale
            old_w, old_h, old_x, old_y = w, h, x, y
            if opt.scale_enable:
                if opt.scale_mode == "random":
                    # Random scaling is relative to the ORIGINAL size.
                    delta = rng.random() * opt.scale_rnd
                    if rng.random() <= 0.5:
                        delta = -delta
                    if opt.scale_dir in ("both", "x"):
                        w = ow + delta
                    if opt.scale_dir in ("both", "y"):
                        h = oh + delta
                elif opt.scale_mode == "pixels":
                    if opt.scale_dir == "both":
                        w = old_w + opt.scale_px
                        h = old_h * (w / old_w)
                    elif opt.scale_dir == "x":
                        w = old_w + opt.scale_px
                    else:
                        h = old_h + opt.scale_px
                else:  # percentage (compounds every step)
                    factor = opt.scale_pr / 100.0
                    if opt.scale_dir in ("both", "x"):
                        w = old_w * factor
                    if opt.scale_dir in ("both", "y"):
                        h = old_h * factor
                w = max(w, MIN_DIM)
                h = max(h, MIN_DIM)

            # Move / grid / anchor
            if move_mode == "horizontal":
                x = old_x + opt.move_inc
                y = old_y - (h - old_h) / 2.0
            elif move_mode == "vertical":
                x = old_x - (w - old_w) / 2.0
                y = old_y + opt.move_inc
            elif move_mode == "diagonal":
                x = old_x + opt.move_inc
                y = old_y + opt.move_inc
            elif move_mode == "random":
                # Scatter within the given region, anchored at the original
                # position (the Sketch original used artboard coordinates).
                x = ox + rng.random() * opt.move_rnd_x
                y = oy + rng.random() * opt.move_rnd_y
            elif grid:
                grid_row_count += 1
                if grid_row_count >= cols:
                    grid_row_count = 0
                    x = grid_x0 - (w - old_w) / 2.0
                    y = grid_y0 + opt.grid_margin_y
                    grid_y0 = y
                else:
                    x = old_x + opt.grid_margin_x
                    y = old_y - (h - old_h) / 2.0
            else:
                # No move: scale from the centre.
                x = old_x - (w - old_w) / 2.0
                y = old_y - (h - old_h) / 2.0

        if opt.hide_original:
            node.style["display"] = "none"

    # ------------------------------------------------------------------

    def opacity_for(self, index, total, rng):
        """Opacity (0..1) for copy `index` (1-based) of `total`, or None."""
        mode = self.options.opacity_mode
        if mode == "random":
            return rng.random()
        if mode == "fadein":
            return min(index * (100.0 / total), 100.0) / 100.0
        if mode == "fadeout":
            return max(100.0 - index * (100.0 / total), 0.0) / 100.0
        return None

    def make_copy(self, node):
        """Deep-copy a node, giving it a fresh id (children lose theirs)."""
        dup = _pycopy.deepcopy(node)
        for child in dup.iter():
            if child is not dup and hasattr(child, "attrib"):
                child.attrib.pop("id", None)
        dup.set("id", self.svg.get_unique_id("looper"))
        return dup

    @staticmethod
    def get_node_matrix(node):
        """The node's own transform as an (a, b, c, d, e, f) tuple."""
        try:
            ((a, c, e), (b, d, f)) = node.transform.matrix
            return (a, b, c, d, e, f)
        except Exception:
            return IDENTITY


if __name__ == "__main__":
    Looper().run()
