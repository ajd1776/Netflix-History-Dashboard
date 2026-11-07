"""The Mac app: the local server shown in a native window instead of a browser tab."""

from __future__ import annotations

from pathlib import Path

import webview

from .local import start_in_background


class Bridge:
    """Called from the page as window.pywebview.api.*"""

    def save_csv(self, content: str, filename: str) -> bool:
        window = webview.windows[0]
        picked = window.create_file_dialog(
            webview.FileDialog.SAVE, save_filename=filename, file_types=("CSV (*.csv)",)
        )
        if not picked:
            return False
        path = picked if isinstance(picked, str) else picked[0]
        Path(path).write_text(content, encoding="utf-8")
        return True


def main() -> None:
    server, url = start_in_background()
    webview.create_window(
        "Netflix History",
        url,
        js_api=Bridge(),
        width=1360,
        height=900,
        min_size=(760, 600),
        background_color="#000000",
    )
    webview.start()
    server.should_exit = True


if __name__ == "__main__":
    main()
