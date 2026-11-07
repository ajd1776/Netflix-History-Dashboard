// Present only inside the Mac app (see api/src/netflix_history_api/desktop.py).
interface Window {
  pywebview?: {
    api: { save_csv(content: string, filename: string): Promise<boolean> }
  }
}
