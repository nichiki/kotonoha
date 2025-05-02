import tempfile
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from typing import Optional

# グローバルなコンソールインスタンス
console = Console()


class ProgressManager:
    """進捗表示を管理するクラス"""
    
    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )
        self.current_task_id: Optional[int] = None
    
    def __enter__(self):
        self.progress.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()
    
    def add_task(self, description: str, total: int) -> int:
        """新しいタスクを追加"""
        self.current_task_id = self.progress.add_task(description, total=total)
        return self.current_task_id
    
    def update(self, advance: int = 1, description: str = None):
        """現在のタスクを更新
        
        Args:
            advance: 進捗を進める量
            description: 更新する説明文（省略可）
        """
        if self.current_task_id is not None:
            update_kwargs = {"advance": advance}
            if description is not None:
                update_kwargs["description"] = description
            self.progress.update(self.current_task_id, **update_kwargs)
            self.progress.refresh()  # 更新後に明示的にリフレッシュ


class TempFileManager:
    """一時ファイルを管理するコンテキストマネージャー"""
    def __init__(self):
        self.temp_dir = None
        self.files = set()

    def __enter__(self):
        """一時ディレクトリの作成"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="kotonoha_"))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 一時ファイルとディレクトリの削除
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_temp_path(self, prefix: str, suffix: str) -> str:
        """一時ファイルのパスを生成"""
        temp_path = self.temp_dir / f"{prefix}{suffix}"
        self.files.add(temp_path)
        return str(temp_path)

    def get_temp_dir(self) -> str:
        """一時ディレクトリのパスを取得"""
        return str(self.temp_dir)


def log_info(message: str):
    """情報メッセージを出力"""
    console.print(f"[blue]ℹ[/blue] {message}")


def log_warning(message: str):
    """警告メッセージを出力"""
    console.print(f"[yellow]⚠[/yellow] {message}")


def log_error(message: str):
    """エラーメッセージを出力"""
    console.print(f"[red]✖[/red] {message}", style="bold red")
