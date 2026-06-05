from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import os
import sys
import platform
import can
import subprocess

IS_WINDOWS = platform.system() == "Windows"


def get_can_bus():
    """Создает CAN-шину в зависимости от ОС"""
    if IS_WINDOWS:
        # Для Windows обычно используется pcan, kvaser или vector
        # Укажите здесь ваш реальный интерфейс и канал!
        return can.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
    else:
        # Для Linux (Orange Pi)
        return can.Bus(interface='socketcan', channel='can0', bitrate=500000)


def main(write_and_read, ui, restart_menu):
    while True:
        test_number = ui(write_and_read)
        
        if test_number == "1":
            console = Console()
            console.print("\n[bold cyan]Инициализация CAN-шины...[/]")
            
            bus = None
            try:
                # Создаем шину
                bus = get_can_bus()
                console.print("[green]Шина открыта. Запуск теста...[/]\n")
                
                # Импортируем тест только в момент запуска (безопаснее для exe)
                from src.tests.test_can import test_can_check_msgs
                
                # Передаем созданную шину в тест
                test_can_check_msgs(bus)
                
                console.print("\n[bold green]✅ Тест успешно завершен![/]")
                
            except ImportError as e:
                console.print(f"\n[bold red]❌ Ошибка импорта теста: {e}[/]")
                console.print("[yellow]Убедитесь, что src/tests/test_can.py существует[/]")
                
            except can.CanError as e:
                console.print(f"\n[bold red]❌ Ошибка CAN: {e}[/]")
                console.print("[yellow]Проверьте подключение адаптера и драйверы[/]")
                
            except AssertionError as e:
                console.print(f"\n[bold red]❌ Assert failed: {e}[/]")
                
            except Exception as e:
                console.print(f"\n[bold red]❌ Неожиданная ошибка: {type(e).__name__}: {e}[/]")
            
            finally:
                # Всегда закрываем шину, даже если тест упал
                if bus is not None:
                    bus.shutdown()
                    console.print("[dim]Шина закрыта.[/]")
                    
            # ️ КРИТИЧНО: Пауза перед возвратом в меню
            input("\nНажмите Enter для продолжения...")

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