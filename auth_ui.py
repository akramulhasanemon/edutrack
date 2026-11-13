"""EduTrack modern glassmorphic sign-in window backed by local SQLite.

Features an ultra-smooth, antialiased academic trajectory forecasting engine with:
- Sub-pixel antialiased Catmull-Rom spline curves via PIL supersampling
- Soft gaussian neon glow and feathered gradient aura under the curve
- Realistic university GPA velocity modeling (BUBT CSE Standard)
- Interactive hover crosshair and glassmorphic tooltip card
- Floating frosted glass containers with specular highlights and glowing badges
- Segmented role switcher and one-click demo presets
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter, ImageTk

from modules.app_icon import set_app_icon
from modules.typography import app_font, maximize_window

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def _catmull_rom_interpolate(
    pts: list[tuple[float, float]], steps_per_segment: int = 30
) -> list[tuple[float, float]]:
    """Generate smooth spline points using Catmull-Rom interpolation."""
    if len(pts) < 2:
        return pts

    def interp(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        t2 = t * t
        t3 = t2 * t
        return 0.5 * (
            (2.0 * p1)
            + (-p0 + p2) * t
            + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
            + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
        )

    dense: list[tuple[float, float]] = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(0, i - 1)]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[min(n - 1, i + 2)]
        for step in range(steps_per_segment):
            t = step / float(steps_per_segment)
            x = interp(p0[0], p1[0], p2[0], p3[0], t)
            y = interp(p0[1], p1[1], p2[1], p3[1], t)
            dense.append((x, y))
    dense.append(pts[-1])
    return dense


class EduTrackLogin(ctk.CTk):
    """Modern dark-themed glassmorphic sign-in screen and trajectory showcase."""

    THEME = {
        # Deep cosmic glass background
        "bg_root": "#050A13",
        "bg_panel_left": "#070E1B",
        "bg_panel_right": "#050A13",
        # Glass card surfaces
        "glass_card": "#0C1729",
        "glass_card_alt": "#101F37",
        "glass_border": "#1C3558",
        "glass_border_glow": "#2B4F83",
        "glass_sheen": "#38BDF8",
        "glass_pill": "#0E1E36",
        "glass_pill_border": "#1B3A66",
        # Input fields
        "input_bg": "#081220",
        "input_border": "#1A3254",
        "input_border_focus": "#38BDF8",
        # Accents & lighting
        "blue": "#2563EB",
        "blue_hover": "#1D4ED8",
        "blue_glow": "#3B82F6",
        "cyan": "#38BDF8",
        "cyan_glow": "#7DD3FC",
        "emerald": "#34D399",
        "emerald_glow": "#10B981",
        "amber": "#FBBF24",
        "red": "#F87171",
        # Typography
        "text_white": "#FFFFFF",
        "text_primary": "#F1F5F9",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "text_dim": "#475569",
    }

    # BUBT CSE realistic academic trajectory data (Organic S-Curve Progression)
    TRAJECTORY_DATA = [
        {
            "sem": "S1",
            "name": "Semester 1 (Fall 2024)",
            "cgpa": 2.85,
            "term": 2.85,
            "credits": 18,
            "status": "Foundational Pace",
            "type": "completed",
            "rel_y": 0.16,
        },
        {
            "sem": "S2",
            "name": "Semester 2 (Spring 2025)",
            "cgpa": 3.05,
            "term": 3.25,
            "credits": 36,
            "status": "Consistent Progress",
            "type": "completed",
            "rel_y": 0.24,
        },
        {
            "sem": "S3",
            "name": "Semester 3 (Fall 2025)",
            "cgpa": 3.24,
            "term": 3.42,
            "credits": 54,
            "status": "Honor Roll Standing",
            "type": "completed",
            "rel_y": 0.35,
        },
        {
            "sem": "S4",
            "name": "Semester 4 (Spring 2026)",
            "cgpa": 3.52,
            "term": 3.78,
            "credits": 72,
            "status": "High Distinction (Current)",
            "type": "current",
            "rel_y": 0.55,
        },
        {
            "sem": "S5",
            "name": "Semester 5 (Fall 2026)",
            "cgpa": 3.72,
            "term": 3.90,
            "credits": 90,
            "status": "Projected Milestone",
            "type": "projected",
            "rel_y": 0.75,
        },
        {
            "sem": "S6",
            "name": "Semester 6 (Spring 2027)",
            "cgpa": 3.88,
            "term": 3.96,
            "credits": 108,
            "status": "Graduation Distinction Target",
            "type": "target",
            "rel_y": 0.92,
        },
    ]

    def __init__(self) -> None:
        super().__init__()
        set_app_icon(self)
        self.title("EduTrack | Academic Intelligence & Workspace Sign In")
        self.geometry("1100x720")
        self.minsize(980, 650)
        maximize_window(self)
        self.configure(fg_color=self.THEME["bg_root"])

        self.authenticated = False
        self.hovered_point_idx: int | None = None
        self._chart_points: list[tuple[float, float]] = []
        self._chart_photo: ImageTk.PhotoImage | None = None

        # 2-column layout
        self.grid_columnconfigure(0, weight=12)
        self.grid_columnconfigure(1, weight=10)
        self.grid_rowconfigure(0, weight=1)

        self._build_brand_panel()
        self._build_login_panel()
        self.bind("<Return>", lambda _event: self._authenticate())

    # =========================================================================
    # LEFT BRAND & TRAJECTORY SHOWCASE
    # =========================================================================

    def _build_brand_panel(self) -> None:
        panel = ctk.CTkFrame(
            self,
            fg_color=self.THEME["bg_panel_left"],
            corner_radius=0,
        )
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        # 1. Top Brand Row (Clean, uncluttered, no 2026 edition badge)
        brand_row = ctk.CTkFrame(panel, fg_color="transparent")
        brand_row.grid(row=0, column=0, sticky="ew", padx=44, pady=(32, 0))

        brand_left = ctk.CTkFrame(brand_row, fg_color="transparent")
        brand_left.pack(side="left")

        # Glass Logo Squircle
        logo_frame = ctk.CTkFrame(
            brand_left,
            width=46,
            height=46,
            corner_radius=14,
            fg_color=self.THEME["blue"],
            border_width=1.5,
            border_color=self.THEME["cyan"],
        )
        logo_frame.pack(side="left", padx=(0, 14))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(
            logo_frame,
            text="E",
            font=app_font(family="Segoe UI", size=24, weight="bold"),
            text_color="white",
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Logo text
        ctk.CTkLabel(
            brand_left,
            text="EduTrack",
            font=app_font(family="Segoe UI", size=24, weight="bold"),
            text_color=self.THEME["text_white"],
        ).pack(side="left")

        # 2. Main Inspiring Headline
        header_frame = ctk.CTkFrame(panel, fg_color="transparent")
        header_frame.grid(row=1, column=0, sticky="w", padx=44, pady=(24, 16))

        ctk.CTkLabel(
            header_frame,
            text="YOUR NEXT CHAPTER,\nBY THE NUMBERS.",
            justify="left",
            font=app_font(family="Segoe UI", size=29, weight="bold"),
            text_color=self.THEME["text_white"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="AI-driven GPA forecasting, semester trajectory modeling, and degree velocity.",
            justify="left",
            font=app_font(family="Segoe UI", size=11),
            text_color=self.THEME["text_secondary"],
        ).pack(anchor="w", pady=(8, 0))

        # 3. Modern Glassmorphic Academic Trajectory Card
        traj_card = ctk.CTkFrame(
            panel,
            fg_color=self.THEME["glass_card"],
            corner_radius=22,
            border_width=1.5,
            border_color=self.THEME["glass_border"],
        )
        traj_card.grid(row=2, column=0, sticky="nsew", padx=44, pady=(0, 22))
        traj_card.grid_columnconfigure(0, weight=1)
        traj_card.grid_rowconfigure(2, weight=1)

        # Specular Sheen Line on top of card
        sheen = ctk.CTkFrame(
            traj_card,
            height=2,
            fg_color=self.THEME["glass_border_glow"],
            corner_radius=1,
        )
        sheen.grid(row=0, column=0, sticky="ew", padx=24, pady=(1, 0))

        # Top Bar of Trajectory Card
        top_bar = ctk.CTkFrame(traj_card, fg_color="transparent")
        top_bar.grid(row=1, column=0, sticky="ew", padx=22, pady=(16, 8))

        # Left title + glowing status
        left_header = ctk.CTkFrame(top_bar, fg_color="transparent")
        left_header.pack(side="left")

        title_pill = ctk.CTkFrame(
            left_header,
            fg_color="#0A1D36",
            border_color="#1E4270",
            border_width=1,
            corner_radius=10,
        )
        title_pill.pack(anchor="w")
        ctk.CTkLabel(
            title_pill,
            text="● ACADEMIC TRAJECTORY ENGINE",
            font=app_font(family="Segoe UI", size=8, weight="bold"),
            text_color=self.THEME["cyan"],
        ).pack(padx=10, pady=3)

        ctk.CTkLabel(
            left_header,
            text="Predictive GPA Curve & Graduation Target",
            font=app_font(family="Segoe UI", size=10),
            text_color=self.THEME["text_muted"],
        ).pack(anchor="w", pady=(4, 0))

        # Right Growth Pill
        growth_pill = ctk.CTkFrame(
            top_bar,
            fg_color="#062E20",
            border_color="#0D593D",
            border_width=1,
            corner_radius=12,
        )
        growth_pill.pack(side="right")
        ctk.CTkLabel(
            growth_pill,
            text="▲ +0.36 GPA PACING",
            font=app_font(family="Segoe UI", size=9, weight="bold"),
            text_color=self.THEME["emerald"],
        ).pack(padx=12, pady=4)

        # Interactive Canvas Chart
        self.chart = ctk.CTkCanvas(
            traj_card,
            background="#081220",
            highlightthickness=0,
            bd=0,
            height=230,
        )
        self.chart.grid(row=2, column=0, sticky="nsew", padx=20, pady=(2, 10))
        self.chart.bind("<Configure>", lambda _event: self._draw_trajectory())
        self.chart.bind("<Motion>", self._on_chart_hover)
        self.chart.bind("<Leave>", self._on_chart_leave)

        # Bottom 3 Glass Metric Cards
        stats_frame = ctk.CTkFrame(traj_card, fg_color="transparent")
        stats_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 16))
        for col in range(3):
            stats_frame.grid_columnconfigure(col, weight=1, uniform="stat_col")

        metric_data = [
            ("CURRENT CGPA", "3.52", "▲ S4 Standing (Top 12%)", self.THEME["cyan"]),
            ("TARGET MILESTONE", "3.88", "★ Magna Cum Laude", self.THEME["emerald"]),
            ("CREDIT VELOCITY", "72 / 142", "51% Degree Completed", self.THEME["text_muted"]),
        ]

        for col, (label, val, sub, accent) in enumerate(metric_data):
            mcard = ctk.CTkFrame(
                stats_frame,
                fg_color=self.THEME["glass_card_alt"],
                border_color=self.THEME["glass_border"],
                border_width=1,
                corner_radius=14,
            )
            mcard.grid(row=0, column=col, sticky="nsew", padx=5)

            ctk.CTkLabel(
                mcard,
                text=label,
                font=app_font(family="Segoe UI", size=8, weight="bold"),
                text_color=self.THEME["text_muted"],
            ).pack(anchor="w", padx=14, pady=(10, 2))

            ctk.CTkLabel(
                mcard,
                text=val,
                font=app_font(family="Segoe UI", size=18, weight="bold"),
                text_color=self.THEME["text_white"],
            ).pack(anchor="w", padx=14, pady=(0, 2))

            ctk.CTkLabel(
                mcard,
                text=sub,
                font=app_font(family="Segoe UI", size=8, weight="bold"),
                text_color=accent,
            ).pack(anchor="w", padx=14, pady=(0, 10))

        # 4. Department Footer
        footer = ctk.CTkFrame(panel, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=44, pady=(0, 18))
        ctk.CTkLabel(
            footer,
            text="BUBT  •  DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING",
            font=app_font(family="Segoe UI", size=9, weight="bold"),
            text_color=self.THEME["text_muted"],
        ).pack(side="left")

    # =========================================================================
    # SILKY-SMOOTH ANTIALIASED ACADEMIC TRAJECTORY RENDERING
    # =========================================================================

    def _draw_trajectory(self) -> None:
        chart = self.chart
        chart.delete("all")
        width = max(chart.winfo_width(), 320)
        height = max(chart.winfo_height(), 160)

        left = 50.0
        right = float(width - 28)
        top = 32.0
        bottom = float(height - 40)

        chart_h = bottom - top
        chart_w = right - left

        # 1. Calculate point coordinates based on organic S-curve progression
        data = self.TRAJECTORY_DATA
        n_points = len(data)
        points: list[tuple[float, float]] = []
        for idx, item in enumerate(data):
            x = left + idx * chart_w / (n_points - 1)
            y = bottom - item["rel_y"] * chart_h
            points.append((x, y))

        self._chart_points = points

        # 2. Render antialiased chart image using PIL with 2x supersampling
        scale = 2
        sw = int(width * scale)
        sh = int(height * scale)
        s_left = left * scale
        s_right = right * scale
        s_top = top * scale
        s_bottom = bottom * scale

        base = Image.new("RGBA", (sw, sh), (8, 18, 32, 255))
        draw_base = ImageDraw.Draw(base)

        scaled_pts = [(p[0] * scale, p[1] * scale) for p in points]
        dense_curve = _catmull_rom_interpolate(scaled_pts, steps_per_segment=40)

        # 2a. Grid Lines & Benchmark
        for g in [0.0, 0.25, 0.50, 0.75, 1.0]:
            gy = s_bottom - g * (s_bottom - s_top)
            for gx in range(int(s_left), int(s_right), 14 * scale):
                draw_base.line([(gx, gy), (gx + 7 * scale, gy)], fill=(20, 38, 62, 170), width=1 * scale)

        by = s_bottom - 0.85 * (s_bottom - s_top)
        for bx in range(int(s_left), int(s_right), 14 * scale):
            draw_base.line([(bx, by), (bx + 7 * scale, by)], fill=(180, 110, 20, 170), width=1 * scale)

        # 2b. Silky Smooth Gradient Aura Under the Curve (Feathered, zero harsh edges)
        area_img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        curve_y_map: dict[int, float] = {}
        for cx, cy in dense_curve:
            ix = int(round(cx))
            if ix not in curve_y_map or cy < curve_y_map[ix]:
                curve_y_map[ix] = cy

        min_x = int(dense_curve[0][0])
        max_x = int(dense_curve[-1][0])
        fade_margin = 45 * scale

        for x_col in range(min_x, max_x + 1):
            if x_col in curve_y_map:
                cy = int(curve_y_map[x_col])
                ey = int(s_bottom)
                span = float(ey - cy) if ey > cy else 1.0
                h_fade = 1.0
                if x_col < min_x + fade_margin:
                    h_fade = (x_col - min_x) / float(fade_margin)
                elif x_col > max_x - fade_margin:
                    h_fade = (max_x - x_col) / float(fade_margin)

                for y_row in range(cy, ey):
                    d = (y_row - cy) / span
                    alpha = int(65 * ((1.0 - d) ** 1.4) * h_fade)
                    r = int(14 + (56 - 14) * (1.0 - d))
                    g = int(60 + (189 - 60) * (1.0 - d))
                    b = int(120 + (248 - 120) * (1.0 - d))
                    area_img.putpixel((x_col, y_row), (r, g, b, alpha))

        area_img = area_img.filter(ImageFilter.GaussianBlur(radius=3 * scale))
        base = Image.alpha_composite(base, area_img)

        # 2c. Soft Gaussian Neon Glow Layer on Spline
        glow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.line(dense_curve, fill=(14, 165, 233, 200), width=6 * scale, joint="curve")
        glow = glow.filter(ImageFilter.GaussianBlur(radius=5 * scale))
        base = Image.alpha_composite(base, glow)

        # 2d. Crisp Antialiased Trajectory Lines
        draw_crisp = ImageDraw.Draw(base)
        idx_s4 = int(len(dense_curve) * 0.60)
        c_curve = dense_curve[:idx_s4 + 1]
        p_curve = dense_curve[idx_s4:]

        # Completed curve (Cyan)
        draw_crisp.line(c_curve, fill=(56, 189, 248, 255), width=int(2.4 * scale), joint="curve")
        draw_crisp.line(c_curve, fill=(240, 249, 255, 230), width=int(1.0 * scale), joint="curve")

        # Projected curve (Emerald transition)
        draw_crisp.line(p_curve, fill=(52, 211, 153, 240), width=int(2.4 * scale), joint="curve")
        draw_crisp.line(p_curve, fill=(236, 253, 245, 230), width=int(1.0 * scale), joint="curve")

        # 2e. Antialiased Milestone Nodes
        for idx, (px, py) in enumerate(scaled_pts):
            is_last = (idx == len(scaled_pts) - 1)
            if is_last: # S6 Goal Beacon
                draw_crisp.ellipse([px - 9*scale, py - 9*scale, px + 9*scale, py + 9*scale], outline=(52, 211, 153, 150), width=1*scale)
                draw_crisp.ellipse([px - 5*scale, py - 5*scale, px + 5*scale, py + 5*scale], fill=(6, 62, 45, 255), outline=(52, 211, 153, 255), width=2*scale)
                draw_crisp.ellipse([px - 2*scale, py - 2*scale, px + 2*scale, py + 2*scale], fill=(255, 255, 255, 255))
            elif idx == 3: # S4 Current Standing
                draw_crisp.ellipse([px - 9*scale, py - 9*scale, px + 9*scale, py + 9*scale], outline=(56, 189, 248, 150), width=1*scale)
                draw_crisp.ellipse([px - 5*scale, py - 5*scale, px + 5*scale, py + 5*scale], fill=(14, 116, 180, 255), outline=(56, 189, 248, 255), width=2*scale)
                draw_crisp.ellipse([px - 2*scale, py - 2*scale, px + 2*scale, py + 2*scale], fill=(255, 255, 255, 255))
            else: # Completed S1, S2, S3 & Projected S5
                col = (52, 211, 153, 220) if idx > 3 else (56, 189, 248, 220)
                draw_crisp.ellipse([px - 5*scale, py - 5*scale, px + 5*scale, py + 5*scale], fill=(8, 26, 46, 255), outline=col, width=int(1.8*scale))
                draw_crisp.ellipse([px - 2*scale, py - 2*scale, px + 2*scale, py + 2*scale], fill=col)

        # 3. Downsample with Lanczos for sub-pixel antialiasing & display
        chart_render = base.resize((width, height), Image.Resampling.LANCZOS)
        self._chart_render_img = chart_render
        self._chart_photo = ImageTk.PhotoImage(chart_render)
        chart.create_image(0, 0, image=self._chart_photo, anchor="nw")

        # 4. Canvas Text Labels & Annotations
        # Benchmark Label
        bench_y = bottom - 0.85 * chart_h
        chart.create_text(
            left + 10,
            bench_y - 8,
            text="★ Dean's Honor Benchmark (3.75)",
            fill="#D97706",
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )

        # Y-Axis Numbers
        y_values = [("2.0", 0.0), ("2.5", 0.25), ("3.0", 0.50), ("3.5", 0.75), ("4.0", 1.0)]
        for label, rel in y_values:
            y_pos = bottom - rel * chart_h
            chart.create_text(
                left - 10,
                y_pos,
                text=label,
                fill=self.THEME["text_muted"],
                font=("Segoe UI", 8),
                anchor="e",
            )

        # Semester X-Axis Labels
        for idx, (x, _y) in enumerate(points):
            item = data[idx]
            is_proj = item["type"] in ("projected", "target")
            col = self.THEME["emerald"] if is_proj else self.THEME["text_secondary"]
            label_text = f"{item['sem']}" + (" (Proj)" if idx == n_points - 1 else "")
            chart.create_text(
                x,
                bottom + 15,
                text=label_text,
                fill=col,
                font=("Segoe UI", 9, "bold" if is_proj else "normal"),
                anchor="n",
            )

        # S4 Floating Current Badge
        s4_x, s4_y = points[3]
        chart.create_line(s4_x, s4_y, s4_x, bottom, fill="#1E4473", width=1.5, dash=(3, 3))
        bw, bh = 104, 23
        bx, by = s4_x - bw / 2, s4_y - 32
        chart.create_rectangle(bx, by, bx + bw, by + bh, fill="#0A1D36", outline=self.THEME["cyan"], width=1)
        chart.create_text(s4_x, by + 12, text=f"CURRENT · {data[3]['cgpa']:.2f}", fill="#FFFFFF", font=("Segoe UI", 8, "bold"))

        # S6 Floating Target Badge
        s6_x, s6_y = points[5]
        chart.create_line(s6_x, s6_y, s6_x, bottom, fill="#0D593D", width=1.5, dash=(3, 3))
        tbw, tbh = 102, 23
        tbx, tby = s6_x - tbw - 4, s6_y - 28
        chart.create_rectangle(tbx, tby, tbx + tbw, tby + tbh, fill="#062E20", outline=self.THEME["emerald"], width=1)
        chart.create_text(tbx + tbw / 2, tby + 12, text=f"★ GOAL · {data[5]['cgpa']:.2f}", fill=self.THEME["emerald"], font=("Segoe UI", 8, "bold"))

        # 5. Interactive Hover Tooltip if hovering over a point
        if self.hovered_point_idx is not None and 0 <= self.hovered_point_idx < len(points):
            h_idx = self.hovered_point_idx
            hx, hy = points[h_idx]
            h_data = data[h_idx]

            # Hover guideline
            chart.create_line(hx, top, hx, bottom, fill=self.THEME["cyan"], width=1.5, dash=(2, 3))

            # Hover node ring
            chart.create_oval(hx - 9, hy - 9, hx + 9, hy + 9, fill="", outline="#FFFFFF", width=2)

            # Floating interactive glass tooltip card
            tt_w, tt_h = 180, 64
            tt_x = min(max(hx - tt_w / 2, left + 4), right - tt_w - 4)
            tt_y = max(hy - tt_h - 14, top + 6)

            # Drop shadow simulation
            chart.create_rectangle(tt_x + 3, tt_y + 3, tt_x + tt_w + 3, tt_y + tt_h + 3, fill="#040912", outline="")
            # Glass body
            chart.create_rectangle(tt_x, tt_y, tt_x + tt_w, tt_y + tt_h, fill="#0E1D33", outline=self.THEME["cyan"], width=1.5)

            # Tooltip content
            chart.create_text(tt_x + 10, tt_y + 13, text=h_data["name"], fill=self.THEME["text_white"], font=("Segoe UI", 8, "bold"), anchor="w")
            chart.create_text(
                tt_x + 10,
                tt_y + 31,
                text=f"CGPA: {h_data['cgpa']:.2f}   |   Term: {h_data['term']:.2f}",
                fill=self.THEME["cyan"],
                font=("Segoe UI", 8, "bold"),
                anchor="w",
            )
            chart.create_text(tt_x + 10, tt_y + 49, text=f"{h_data['status']} • {h_data['credits']} Cr", fill=self.THEME["text_secondary"], font=("Segoe UI", 7), anchor="w")

    def _on_chart_hover(self, event: Any) -> None:
        """Detect nearest trajectory point for interactive inspection."""
        if not self._chart_points:
            return
        mx = event.x
        nearest_idx = None
        min_dist = float("inf")
        for idx, (px, _py) in enumerate(self._chart_points):
            dist = abs(mx - px)
            if dist < min_dist and dist < 36:
                min_dist = dist
                nearest_idx = idx

        if nearest_idx != self.hovered_point_idx:
            self.hovered_point_idx = nearest_idx
            self._draw_trajectory()

    def _on_chart_leave(self, _event: Any) -> None:
        """Clear hover tooltip when mouse leaves the chart."""
        if self.hovered_point_idx is not None:
            self.hovered_point_idx = None
            self._draw_trajectory()

    # =========================================================================
    # RIGHT FLOATING GLASS LOGIN PANEL
    # =========================================================================

    def _build_login_panel(self) -> None:
        panel = ctk.CTkFrame(self, fg_color=self.THEME["bg_panel_right"], corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew", padx=36, pady=24)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        # Centered Floating Glassmorphic Login Card
        glass_card = ctk.CTkFrame(
            panel,
            fg_color=self.THEME["glass_card"],
            corner_radius=24,
            border_width=1.5,
            border_color=self.THEME["glass_border"],
        )
        glass_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88)

        # Specular Sheen line on top of login card
        sheen = ctk.CTkFrame(
            glass_card,
            height=2,
            fg_color=self.THEME["glass_border_glow"],
            corner_radius=1,
        )
        sheen.pack(fill="x", padx=24, pady=(1, 0))

        inner = ctk.CTkFrame(glass_card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=(24, 28))

        # 1. Top Gateway Pill
        top_pill = ctk.CTkFrame(
            inner,
            fg_color=self.THEME["glass_pill"],
            border_color=self.THEME["glass_pill_border"],
            border_width=1,
            corner_radius=12,
        )
        top_pill.pack(anchor="w")
        ctk.CTkLabel(
            top_pill,
            text="✦ SECURE ACADEMIC WORKSPACE",
            font=app_font(family="Segoe UI", size=8, weight="bold"),
            text_color=self.THEME["cyan"],
        ).pack(padx=12, pady=3)

        # 2. Card Title & Subtitle
        ctk.CTkLabel(
            inner,
            text="Sign In to EduTrack",
            font=app_font(family="Segoe UI", size=26, weight="bold"),
            text_color=self.THEME["text_white"],
        ).pack(anchor="w", pady=(10, 4))

        ctk.CTkLabel(
            inner,
            text="Access your academic records, forecasting tools, and advising.",
            font=app_font(family="Segoe UI", size=10),
            text_color=self.THEME["text_secondary"],
        ).pack(anchor="w", pady=(0, 20))

        # 3. Modern Segmented Role Selector
        self._field_label(inner, "SELECT WORKSPACE ROLE")
        self.role_selector = ctk.CTkSegmentedButton(
            inner,
            values=["Student", "Faculty"],
            height=42,
            corner_radius=11,
            fg_color=self.THEME["input_bg"],
            selected_color=self.THEME["blue"],
            selected_hover_color=self.THEME["blue_hover"],
            unselected_color=self.THEME["input_bg"],
            unselected_hover_color=self.THEME["glass_card_alt"],
            text_color=self.THEME["text_white"],
            font=app_font(family="Segoe UI", size=11, weight="bold"),
            command=self._on_role_switched,
        )
        self.role_selector.pack(fill="x", pady=(0, 16))
        self.role_selector.set("Student")

        # 4. Institutional ID Entry
        self.id_label = self._field_label(inner, "STUDENT ID")
        self.user_id = ctk.CTkEntry(
            inner,
            height=44,
            corner_radius=11,
            border_width=1.5,
            border_color=self.THEME["input_border"],
            fg_color=self.THEME["input_bg"],
            text_color=self.THEME["text_white"],
            placeholder_text="Enter your institutional ID",
            placeholder_text_color=self.THEME["text_dim"],
            font=app_font(family="Segoe UI", size=11),
        )
        self.user_id.pack(fill="x", pady=(0, 14))
        self.user_id.insert(0, "20255103311")

        # 5. Password Entry with Show/Hide Toggle
        self._field_label(inner, "PASSWORD")
        pw_box = ctk.CTkFrame(inner, fg_color="transparent")
        pw_box.pack(fill="x", pady=(0, 8))

        self.password = ctk.CTkEntry(
            pw_box,
            height=44,
            corner_radius=11,
            border_width=1.5,
            border_color=self.THEME["input_border"],
            fg_color=self.THEME["input_bg"],
            text_color=self.THEME["text_white"],
            placeholder_text="Enter your account password",
            placeholder_text_color=self.THEME["text_dim"],
            show="•",
            font=app_font(family="Segoe UI", size=11),
        )
        self.password.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.password.insert(0, "EduTrack2026!")

        self.pw_visible = False
        self.show_pw_btn = ctk.CTkButton(
            pw_box,
            text="👁",
            width=44,
            height=44,
            corner_radius=11,
            fg_color=self.THEME["input_bg"],
            hover_color=self.THEME["glass_card_alt"],
            border_width=1.5,
            border_color=self.THEME["input_border"],
            font=app_font(family="Segoe UI", size=12),
            command=self._toggle_password_visibility,
        )
        self.show_pw_btn.pack(side="right")

        # 6. Status / Validation Message
        self.status = ctk.CTkLabel(
            inner,
            text="",
            height=24,
            anchor="w",
            wraplength=350,
            justify="left",
            font=app_font(family="Segoe UI", size=10),
            text_color=self.THEME["red"],
        )
        self.status.pack(fill="x", pady=(0, 6))

        # 7. Primary Glowing Sign In Button
        self.login_button = ctk.CTkButton(
            inner,
            text="Sign In to Workspace   →",
            height=48,
            corner_radius=12,
            fg_color=self.THEME["blue"],
            hover_color=self.THEME["blue_hover"],
            border_width=1,
            border_color=self.THEME["cyan"],
            font=app_font(family="Segoe UI", size=12, weight="bold"),
            command=self._authenticate,
        )
        self.login_button.pack(fill="x", pady=(0, 16))

        # 8. Quick Demo Presets Bar
        demo_box = ctk.CTkFrame(
            inner,
            fg_color=self.THEME["glass_pill"],
            border_color=self.THEME["glass_pill_border"],
            border_width=1,
            corner_radius=12,
        )
        demo_box.pack(fill="x", pady=(0, 10))

        demo_inner = ctk.CTkFrame(demo_box, fg_color="transparent")
        demo_inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            demo_inner,
            text="⚡ QUICK DEMO ACCESS",
            font=app_font(family="Segoe UI", size=8, weight="bold"),
            text_color=self.THEME["cyan"],
        ).pack(anchor="w", pady=(0, 6))

        quick_btn_frame = ctk.CTkFrame(demo_inner, fg_color="transparent")
        quick_btn_frame.pack(fill="x")
        quick_btn_frame.grid_columnconfigure(0, weight=1)
        quick_btn_frame.grid_columnconfigure(1, weight=1)

        student_btn = ctk.CTkButton(
            quick_btn_frame,
            text="🎓 Student Demo",
            height=32,
            corner_radius=8,
            fg_color=self.THEME["input_bg"],
            hover_color=self.THEME["glass_card_alt"],
            border_width=1,
            border_color=self.THEME["input_border"],
            text_color=self.THEME["text_primary"],
            font=app_font(family="Segoe UI", size=9, weight="bold"),
            command=self._fill_student_demo,
        )
        student_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        faculty_btn = ctk.CTkButton(
            quick_btn_frame,
            text="🏛️ Faculty Demo",
            height=32,
            corner_radius=8,
            fg_color=self.THEME["input_bg"],
            hover_color=self.THEME["glass_card_alt"],
            border_width=1,
            border_color=self.THEME["input_border"],
            text_color=self.THEME["text_primary"],
            font=app_font(family="Segoe UI", size=9, weight="bold"),
            command=self._fill_faculty_demo,
        )
        faculty_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Footnote
        ctk.CTkLabel(
            inner,
            text="🔒 Local SQLite Storage  •  BUBT CSE Standard CGPA Modeling",
            font=app_font(family="Segoe UI", size=8),
            text_color=self.THEME["text_dim"],
            justify="center",
        ).pack(anchor="center", pady=(4, 0))

    # =========================================================================
    # HELPERS & AUTHENTICATION
    # =========================================================================

    def _field_label(self, parent: ctk.CTkFrame, text: str) -> ctk.CTkLabel:
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=app_font(family="Segoe UI", size=9, weight="bold"),
            text_color=self.THEME["text_secondary"],
        )
        label.pack(anchor="w", pady=(0, 6))
        return label

    def _on_role_switched(self, role: str) -> None:
        """Update placeholder text and label dynamically when role changes."""
        if role == "Faculty":
            self.id_label.configure(text="FACULTY ID")
            if self.user_id.get() == "20255103311":
                self.user_id.delete(0, "end")
                self.user_id.insert(0, "FAC-2026-CSE")
            self.user_id.configure(placeholder_text="Enter your Faculty ID")
        else:
            self.id_label.configure(text="STUDENT ID")
            if self.user_id.get() == "FAC-2026-CSE":
                self.user_id.delete(0, "end")
                self.user_id.insert(0, "20255103311")
            self.user_id.configure(placeholder_text="Enter your institutional Student ID")

    def _fill_student_demo(self) -> None:
        """Autofill student demo credentials."""
        self.role_selector.set("Student")
        self._on_role_switched("Student")
        self.user_id.delete(0, "end")
        self.user_id.insert(0, "20255103311")
        self.password.delete(0, "end")
        self.password.insert(0, "EduTrack2026!")
        self.status.configure(text="")

    def _fill_faculty_demo(self) -> None:
        """Autofill faculty demo credentials."""
        self.role_selector.set("Faculty")
        self._on_role_switched("Faculty")
        self.user_id.delete(0, "end")
        self.user_id.insert(0, "FAC-2026-CSE")
        self.password.delete(0, "end")
        self.password.insert(0, "EduTrack2026!")
        self.status.configure(text="")

    def _toggle_password_visibility(self) -> None:
        """Toggle between masking and showing the password."""
        self.pw_visible = not self.pw_visible
        if self.pw_visible:
            self.password.configure(show="")
            self.show_pw_btn.configure(text="🔒")
        else:
            self.password.configure(show="•")
            self.show_pw_btn.configure(text="👁")

    def _authenticate(self) -> None:
        """Validate input and launch the main EduTrack dashboard."""
        user_id = self.user_id.get().strip()
        password = self.password.get()
        role = self.role_selector.get()

        if not user_id or not password:
            self._show_status(
                "Please enter both your institutional ID and password.",
                self.THEME["red"],
            )
            return

        display_name = "Faculty Member" if role == "Faculty" else "CSE Student"
        os.environ["EDUTRACK_USER_ID"] = user_id
        os.environ["EDUTRACK_USER_NAME"] = display_name
        os.environ["EDUTRACK_USER_ROLE"] = role
        os.environ["EDUTRACK_AUTHENTICATED"] = "1"
        self.authenticated = True
        self.destroy()

    def _show_status(self, text: str, color: str) -> None:
        self.status.configure(text=text, text_color=color)


if __name__ == "__main__":
    while True:
        app = EduTrackLogin()
        app.mainloop()
        if not getattr(app, "authenticated", False):
            break

        from main import EduTrackApp

        main_app = EduTrackApp()
        main_app.mainloop()
        if getattr(main_app, "signed_out", False):
            os.environ["EDUTRACK_AUTHENTICATED"] = "0"
            continue
        break
