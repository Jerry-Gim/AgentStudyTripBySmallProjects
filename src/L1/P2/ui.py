"""
彩色输出隔离层，无 rich 自动降级
"""

# 尝试导入rich，如果不支持回退回黑白
try:
    from rich.console import Console
    from rich.color import Color
    from rich.table import Table
    from rich.text import Text
    RICH_OK = True
except ModuleNotFoundError:
    RICH_OK = False

# 单例控制台
console = Console() if RICH_OK else None

def color_temp(temp: float) -> str:
    """给温度加颜色，返回 str"""
    if not RICH_OK:
        return f"{temp}℃"
    # 自定义色阶
    if temp >= 30:
        color = "red"
    elif temp >= 20:
        color = "green"
    elif temp >= 10:
        color = "yellow"
    else:
        color = "blue"
    return str(Text(f"{temp}℃", style=color))

def print_table(title: str, rows: list[tuple]) -> None:
    """把 [(时间, 温度, 天气), ...] 打成彩色表"""
    if not RICH_OK:
        for r in rows:
            print("  ".join(r))
        return
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("时间", style="dim")
    table.add_column("温度", justify="right")
    table.add_column("天气")
    for t, tmp, desc in rows:
        table.add_row(t, color_temp(float(tmp)), desc)
    console.print(table)

def print_current(city: str, weather: str, temp: float, temp_max: float,
                  humidity: int, wind: float, unit_label: str, feel: str) -> None:
    """当前天气彩色一句话"""
    if not RICH_OK:
        txt = (f"{city}  今天 {weather}  "
               f"{temp}℃↑{temp_max}℃  "
               f"湿度{humidity}%  风速{wind}{unit_label}  体感{feel}")
        print(txt)
        return
    console.print()
    console.print(f"[bold]{city}[/]  今天 [cyan]{weather}[/]  "
                  f"{color_temp(temp)}↑{color_temp(temp_max)}  "
                  f"湿度[bright_black]{humidity}%[/]  "
                  f"风速[bright_black]{wind}{unit_label}[/]  "
                  f"体感[bold]{feel}[/]")