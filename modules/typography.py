"""Shared readable typography for the EduTrack desktop interfaces."""

from __future__ import annotations

# Lazy import customtkinter only if legacy font helpers are called
import tkinter as tk


DEFAULT_ACCENT_THEME = "Default Blue"

ACCENT_THEMES = {
    "Default Blue": {
        "primary": "#2563EB",
        "primary_hover": "#1D4ED8",
        "accent": "#38BDF8",
        "card": "#0C1729",
        "card_alt": "#101F37",
    },
    "Emerald": {
        "primary": "#10B981",
        "primary_hover": "#059669",
        "accent": "#34D399",
        "card": "#091D17",
        "card_alt": "#0E2920",
    },
    "Purple": {
        "primary": "#8B5CF6",
        "primary_hover": "#7C3AED",
        "accent": "#C4B5FD",
        "card": "#141026",
        "card_alt": "#1C1736",
    },
}


def accent_theme_colors(theme_name: str) -> dict[str, str]:
    """Return the accent and card colors for a supported application theme."""
    try:
        palette = ACCENT_THEMES[theme_name]
    except KeyError as exc:
        raise ValueError(f"Unknown accent theme: {theme_name!r}.") from exc
    return {
        "blue": palette["primary"],
        "blue_hover": palette["primary_hover"],
        "cyan": palette["accent"],
        "surface": palette["card"],
        "surface_alt": palette["card_alt"],
    }


_FONT_SIZE_SCALE = {
    8: 11,
    9: 12,
    10: 13,
    11: 14,
    12: 15,
    13: 16,
    14: 18,
    15: 19,
    16: 20,
    17: 21,
}


def readable_font_size(size: int) -> int:
    """Map compact legacy sizes to legible UI sizes while preserving display fonts."""
    return _FONT_SIZE_SCALE.get(size, size)


def app_font(
    *, size: int, family: str = "Segoe UI", weight: str = "normal"
):
    """Create an application font using the shared accessible size scale."""
    import customtkinter as ctk
    readable_size = readable_font_size(size)
    return ctk.CTkFont(family=family, size=readable_size, weight=weight)


def maximize_window(window) -> None:
    """Open window maximized across platforms (Windows 'zoomed', Linux/Mac fallback).
    Also binds F11 to toggle borderless fullscreen and Escape to return to maximized mode.
    """
    is_fullscreen = False

    def apply_maximize() -> None:
        if is_fullscreen:
            return
        try:
            window.state("zoomed")
        except tk.TclError:
            try:
                window.attributes("-zoomed", True)
            except tk.TclError:
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()
                window.geometry(f"{screen_width}x{screen_height}+0+0")

    # Apply immediately and after CustomTkinter finishes initial drawing/mapping
    apply_maximize()
    window.after(50, apply_maximize)
    window.after(200, apply_maximize)

    def enter_fullscreen() -> None:
        nonlocal is_fullscreen
        try:
            window.attributes("-fullscreen", True)
            is_fullscreen = True
        except tk.TclError:
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            window.geometry(f"{screen_width}x{screen_height}+0+0")
            is_fullscreen = True

    def exit_fullscreen() -> None:
        nonlocal is_fullscreen
        try:
            window.attributes("-fullscreen", False)
        except tk.TclError:
            pass
        is_fullscreen = False
        apply_maximize()

    def toggle_fullscreen(_event: tk.Event | None = None) -> str:
        nonlocal is_fullscreen
        if is_fullscreen:
            exit_fullscreen()
        else:
            enter_fullscreen()
        return "break"

    def escape_fullscreen(_event: tk.Event | None = None) -> str:
        if is_fullscreen:
            exit_fullscreen()
        return "break"

    window.bind_all("<F11>", toggle_fullscreen)
    window.bind_all("<Escape>", escape_fullscreen)
