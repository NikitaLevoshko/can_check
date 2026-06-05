from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import os
import sys
import subprocess
import platform

IS_WINDOWS = platform.system() == "Windows"

def resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу (работает и для .exe, и для скрипта)"""
    if getattr(sys, 'frozen', False):
        # Запущен как .exe — файлы во временной папке
        base_path = sys._MEIPASS
    else:
        # Запущен как скрипт — файлы рядом
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def main(write_and_read, ui, restart_menu):
    while True:
        test_number = ui(write_and_read)
        if test_number == "1":
            test_file = resource_path("src/tests/test_can.py")
            test_dir = os.path.dirname(test_file)
            
            # Устанавливаем PYTHONPATH, чтобы pytest видел все модули внутри exe
            env = os.environ.copy()
            if getattr(sys, 'frozen', False):
                # Добавляем корень временной папки _MEIPASS в путь поиска
                env['PYTHONPATH'] = sys._MEIPASS
            
            
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v"],
                cwd=test_dir,
                env=env  # Передаём модифицированное окружение
            )
                 
        elif test_number == "00":
            break
        elif test_number == "0":
            pass
        else:
            print("Повторите запуск с релевантным вводом")
        
        if restart_menu() == 1:
            break


def restart_menu():
    # Переименовали переменную, чтобы не перекрывать имя функции
    should_exit = 0 
    instruction_text = Text()
    instruction_text.append("Для перезапуска меню нажмите ", style="white")
    instruction_text.append("1\n", style="bold cyan")
    instruction_text.append("Для выхода нажмите ", style="white")
    instruction_text.append("00", style="bold cyan")
    
    console = Console()
    console.print(
        Panel(
            instruction_text,
            title="[bold white]ПЕРЕЗАПУСК[/]",
            border_style="yellow",
            padding=(1, 2),
        )
    )
    return_number = Prompt.ask("Ваш выбор")
    if return_number == "00":
        should_exit = 1
    return should_exit


def write_and_read(command, workdir="."):
    if isinstance(command, str):
        command = command.split()
    result = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", cwd=workdir
    )
    return result.stdout


def clear_screen():
    os.system("cls" if IS_WINDOWS else "clear")


def ui(write_and_read):
    clear_screen()

    console = Console()
    table = Table()

    table.add_column("Модуль", justify="left", style="cyan", width=10)
    table.add_column("Состояние", style="bold", width=20)
    table.add_column("Возможный метод исправления", width=30)
    table.add_column("Примечание", justify="left", style="green", width=15)

    # Пустая строка добавляется без ошибок, как вы и указали
    table.add_row("", "", "", "") 

    console.print(
        Panel(table, title="СОСТОЯНИЕ СИСТЕМЫ ТЕСТИРОВАНИЯ", border_style="white")
    )

    instruction_text = Text()
    instruction_text.append("Для тестирования ", style="white")
    instruction_text.append("can", style="bold cyan")
    instruction_text.append(" введите ", style="white")
    instruction_text.append("1\n", style="bold cyan")
    instruction_text.append("Для выхода введите ", style="white")
    instruction_text.append("00\n", style="bold cyan")
    instruction_text.append("Для перезапуска меню введите ", style="white")
    instruction_text.append("0", style="bold cyan")

    console.print(
        Panel(
            instruction_text,
            title="[bold white]ВЫБОР ТЕСТИРУЕМОГО МОДУЛЯ[/]",
            border_style="yellow",
            padding=(1, 2),
        )
    )

    test_number = Prompt.ask("Ваш выбор")
    return test_number


def status_color(state):
    if "не" in state.lower():
        return Text(state, style="bold red")
    else:
        return Text(state, style="bold green")


def solve_color(solve):
    if "не требуются" in solve.lower():
        return Text(solve, style="bold green")
    else:
        return Text(solve, style="bold red")


if __name__ == "__main__":
    main(write_and_read, ui, restart_menu)