import typer
import time
from datetime import datetime
import okosu
from okosu.core import transcribe_audio
from okosu.utils import console

app = typer.Typer()

@app.command()
def transcribe(
    input_path: str = typer.Argument(..., help="Path to audio file to transcribe"),
    format: str = typer.Option(None, "--format", "-f", help="Output format (srt/txt)")
):
    """Run transcription pipeline and output in specified format."""
    start_time = time.time()
    start_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        output_path = transcribe_audio(input_path, output_format=format)
        
        # 処理時間の表示
        end_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_time = time.time() - start_time
        
        # 結果サマリーの表示
        console.print("\n[green]処理成功[/green] 🎉")
        console.print(f"[bold]出力ファイル:[/bold] {output_path}")
        console.print("\n[bold]処理時間:[/bold]")
        console.print(f"  開始: {start_str}")
        console.print(f"  終了: {end_str}")
        console.print(f"  所要: {total_time:.2f} 秒")
        
    except Exception as e:
        console.print(f"[red]エラーが発生しました: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def version():
    """Show the version of okosu CLI."""
    console.print(f"[bold]okosu[/bold] version [blue]{okosu.__version__}[/blue]")

if __name__ == "__main__":
    app()