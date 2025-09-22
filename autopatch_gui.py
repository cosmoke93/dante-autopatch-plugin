"""
Dante AI Autopatch - GUI Edition

This module provides a graphical interface for the Dante AI Autopatch system.
It is built using Tkinter (included in the Python standard library) so it
requires no additional third‑party packages. On startup the program scans
for Dante devices on the local network (falling back to a simulated set if
no Dante Application Library is installed)【551168751628221†L24-L45】.  It then displays
the devices and a list of suggested patch routings.  Users can review the
patch suggestions and click a single button to apply them.  When run under
Windows the script can be bundled into a standalone executable using
PyInstaller or built automatically via the provided GitHub Actions workflow.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Device:
    """Represents a generic Dante device on the network."""
    name: str
    role: str  # e.g. "console", "stagebox", "amplifier", "monitor"
    channels_in: int
    channels_out: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.name} ({self.role}, IN:{self.channels_in}, OUT:{self.channels_out})"


class DeviceScanner:
    """
    Discovers Dante devices on the network, with fallback to simulation.

    If the official Dante Application Library (DAL) is installed, this class
    uses it to discover real devices and populate Device objects accordingly.
    Otherwise, it returns a simulated list of common devices.  This fallback
    ensures the GUI remains functional even without network access【551168751628221†L24-L45】.
    """
    try:
        # Replace this import with the actual DAL import when available
        from dante_application_library import DeviceScanner as DALDeviceScanner  # type: ignore
        DAL_AVAILABLE = True
    except Exception:
        DALDeviceScanner = None  # type: ignore
        DAL_AVAILABLE = False

    @staticmethod
    def discover_devices() -> List[Device]:
        devices: List[Device] = []
        # If DAL is installed and importable, use it
        if DeviceScanner.DAL_AVAILABLE and DeviceScanner.DALDeviceScanner:
            try:
                dal_scanner = DeviceScanner.DALDeviceScanner()
                dal_devices = dal_scanner.discover_devices()  # hypothetical API
                for d in dal_devices:
                    devices.append(
                        Device(
                            name=getattr(d, "name", "Unknown Device"),
                            role=getattr(d, "role", "unknown"),
                            channels_in=getattr(d, "channels_in", 0),
                            channels_out=getattr(d, "channels_out", 0),
                            metadata={"dal_id": getattr(d, "id", ""), "raw": d},
                        )
                    )
            except Exception as e:
                print(f"[WARN] DAL discovery failed: {e}; falling back to simulation.")

        if not devices:
            # Simulated devices as fallback
            devices = [
                Device(name="Yamaha TF1", role="console", channels_in=32, channels_out=16),
                Device(name="Yamaha Rio3224-D2", role="stagebox", channels_in=32, channels_out=24),
                Device(name="LA12X", role="amplifier", channels_in=2, channels_out=4),
                Device(name="Shure Axient", role="monitor", channels_in=8, channels_out=8),
            ]
        return devices


class PatchSuggestion:
    """Represents a suggested routing between two devices."""
    def __init__(self, source: Device, destination: Device, description: str) -> None:
        self.source = source
        self.destination = destination
        self.description = description

    def __repr__(self) -> str:
        return f"{self.description}: {self.source.name} → {self.destination.name}"


class AutoPatchEngine:
    """
    Generates and applies patch suggestions.

    The engine analyses the list of available devices and proposes routings
    based on simple heuristics: stageboxes feed consoles, consoles feed
    amplifiers and monitors.  When applying a patch the engine will attempt
    to use the DAL API if available, otherwise it simply prints the routes.
    """
    def __init__(self, devices: List[Device]) -> None:
        self.devices = devices

    def generate_suggestions(self) -> List[PatchSuggestion]:
        suggestions: List[PatchSuggestion] = []
        consoles = [d for d in self.devices if d.role == "console"]
        stageboxes = [d for d in self.devices if d.role == "stagebox"]
        amplifiers = [d for d in self.devices if d.role == "amplifier"]
        monitors = [d for d in self.devices if d.role == "monitor"]
        for stagebox in stageboxes:
            for console in consoles:
                suggestions.append(PatchSuggestion(stagebox, console, "Route stagebox → console"))
        for console in consoles:
            for amp in amplifiers:
                suggestions.append(PatchSuggestion(console, amp, "Route console → amplifier"))
        for console in consoles:
            for mon in monitors:
                suggestions.append(PatchSuggestion(console, mon, "Route console → monitor"))
        return suggestions

    def apply_patch(self, suggestions: List[PatchSuggestion]) -> None:
        # Attempt to apply via DAL if available (placeholder). Otherwise, print.
        if DeviceScanner.DAL_AVAILABLE and DeviceScanner.DALDeviceScanner:
            try:
                for sugg in suggestions:
                    src = sugg.source
                    dst = sugg.destination
                    # Insert real subscription call here using DAL API
                    print(f"[DAL] Subscribing {src.name} → {dst.name}")
                return
            except Exception as e:
                print(f"[WARN] DAL patch failed: {e}; printing routes.")
        # Print routes
        print("Applying patch routes:")
        for sugg in suggestions:
            print(f" - {sugg}")


class AutopatchGUI(tk.Tk):
    """Main window for the Autopatch graphical interface."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Dante AI Autopatch")
        # Modern dark theme colors
        self.configure(bg="#181a1f")

        # Discover devices and generate suggestions
        self.devices: List[Device] = DeviceScanner.discover_devices()
        self.engine = AutoPatchEngine(self.devices)
        self.suggestions: List[PatchSuggestion] = self.engine.generate_suggestions()

        # Build UI
        self._build_widgets()

    def _build_widgets(self) -> None:
        # Title label
        title = tk.Label(
            self,
            text="Dante AI Autopatch",
            font=("Segoe UI", 18, "bold"),
            fg="#00bfff",
            bg="#181a1f",
        )
        title.pack(pady=(10, 5))

        subtitle = tk.Label(
            self,
            text="Sélectionnez un routage suggéré et appliquez-le",
            font=("Segoe UI", 10),
            fg="#a5adbb",
            bg="#181a1f",
        )
        subtitle.pack(pady=(0, 10))

        container = tk.Frame(self, bg="#181a1f")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel: device list
        device_frame = tk.Frame(container, bg="#1e2127", bd=1, relief=tk.RIDGE)
        device_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        device_title = tk.Label(
            device_frame,
            text="Appareils détectés",
            font=("Segoe UI", 12, "bold"),
            fg="#00bfff",
            bg="#1e2127",
        )
        device_title.pack(fill=tk.X, padx=5, pady=5)
        self.device_list = tk.Listbox(
            device_frame,
            bg="#2c303a",
            fg="#ffffff",
            selectbackground="#00bfff",
            selectforeground="#000000",
            highlightthickness=0,
            borderwidth=0,
        )
        # Populate device list
        for dev in self.devices:
            self.device_list.insert(tk.END, str(dev))
        self.device_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Right panel: suggestions
        suggest_frame = tk.Frame(container, bg="#1e2127", bd=1, relief=tk.RIDGE)
        suggest_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        suggest_title = tk.Label(
            suggest_frame,
            text="Routages suggérés",
            font=("Segoe UI", 12, "bold"),
            fg="#00bfff",
            bg="#1e2127",
        )
        suggest_title.pack(fill=tk.X, padx=5, pady=5)
        self.suggest_list = tk.Listbox(
            suggest_frame,
            bg="#2c303a",
            fg="#ffffff",
            selectbackground="#00bfff",
            selectforeground="#000000",
            highlightthickness=0,
            borderwidth=0,
        )
        for s in self.suggestions:
            self.suggest_list.insert(tk.END, repr(s))
        self.suggest_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # Apply button
        btn = tk.Button(
            self,
            text="Appliquer le patch",
            font=("Segoe UI", 12, "bold"),
            bg="#00bfff",
            fg="#181a1f",
            activebackground="#0095c7",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            command=self._on_apply,
            padx=10,
            pady=5,
        )
        btn.pack(pady=10)

    def _on_apply(self) -> None:
        """Handle click on the apply button."""
        self.engine.apply_patch(self.suggestions)
        messagebox.showinfo(
            "Patch appliqué",
            "Les routages suggérés ont été appliqués (ou simulés).",
        )


def main() -> None:
    app = AutopatchGUI()
    app.geometry("800x500")
    app.mainloop()


if __name__ == "__main__":
    main()
