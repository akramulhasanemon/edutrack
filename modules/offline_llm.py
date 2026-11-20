"""EduTrack Embedded Offline Generative LLM Engine.

Directly drives standalone llama-cli binary with local GGUF models:
- 100% On-Device AVX2 multithreaded CPU inference (AMD Ryzen 12-thread optimized)
- Zero external software dependencies (Self-contained in d:/EduTrack/bin and d:/EduTrack/models)
- Generates intelligent, real-time responses for ANY coding, theory, or academic query
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

class EmbeddedOfflineLLM:
    """Self-contained on-device generative LLM runner for EduTrack."""

    _instance: EmbeddedOfflineLLM | None = None

    def __init__(self) -> None:
        self.root_dir = Path(__file__).resolve().parent.parent
        self.bin_dir = self.root_dir / "bin"
        self.models_dir = self.root_dir / "models"
        self.cli_exe = self.bin_dir / "llama-cli.exe"
        self.default_model = self.models_dir / "llama-3.2-1b-instruct-q4_k_m.gguf"

    @classmethod
    def get_instance(cls) -> EmbeddedOfflineLLM:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def is_available(self) -> bool:
        """Check if both the runner binary and GGUF model exist and are ready."""
        if not self.cli_exe.exists():
            return False
        model = self.get_model_path()
        return model is not None and model.exists() and os.path.getsize(model) > 50 * 1024 * 1024

    def get_model_path(self) -> Path | None:
        if self.default_model.exists() and os.path.getsize(self.default_model) > 50 * 1024 * 1024:
            return self.default_model
        ggufs = list(self.models_dir.glob("*.gguf"))
        if ggufs and os.path.getsize(ggufs[0]) > 50 * 1024 * 1024:
            return ggufs[0]
        return None

    def generate(
        self,
        prompt: str,
        system_instruction: str = "",
        max_tokens: int = 350,
        temperature: float = 0.7,
        threads: int = 8
    ) -> str | None:
        """Runs the standalone llama-cli binary with multithreaded AVX2 inference."""
        model_path = self.get_model_path()
        if not model_path or not self.cli_exe.exists():
            return None

        cmd = [
            str(self.cli_exe),
            "-m", str(model_path),
            "-p", prompt,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "-t", str(threads),
            "-st",
            "--no-display-prompt",
        ]

        if system_instruction:
            cmd.extend(["-sys", system_instruction])

        env = os.environ.copy()
        env["PATH"] = str(self.bin_dir) + os.pathsep + env.get("PATH", "")

        try:
            res = subprocess.run(
                cmd,
                cwd=str(self.bin_dir),
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=45,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            raw_output = res.stdout.strip()
            if not raw_output:
                return None

            lines = raw_output.splitlines()
            content_lines = []
            capturing = False

            for line in lines:
                if line.startswith("> "):
                    capturing = True
                    continue
                if capturing:
                    if line.startswith("[ Prompt:") or line.strip() == "Exiting...":
                        break
                    content_lines.append(line)

            parsed = "\n".join(content_lines).strip()
            if not parsed:
                # Fallback: strip header keywords
                filtered = [
                    l for l in lines
                    if not any(l.startswith(k) for k in (
                        "Loading model", "build", "model", "ftype", "modalities",
                        "available commands", "/exit", "/regen", "/clear", "/read", "/glob",
                        "[ Prompt:", "Exiting", "▄", "█", "using custom system prompt"
                    ))
                ]
                parsed = "\n".join(filtered).strip()

            for token in ("<|eot_id|>", "<|end_of_text|>", "<|start_header_id|>", "<|begin_of_text|>"):
                parsed = parsed.replace(token, "")

            return parsed.strip() if len(parsed.strip()) > 5 else None

        except Exception:
            return None
