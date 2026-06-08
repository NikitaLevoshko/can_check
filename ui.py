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
import time
import threading

IS_WINDOWS = platform.system() == "Windows"


def run_test_infinite(bus, console, stop_event):
    """Функция для запуска теста в бесконечном цикле"""
    from src.tests.test_can import test_can_check_msgs
    
    while not stop_event.is_set():
        try:
            console.print("[cyan]Запуск новой итерации теста...[/]")
            test_can_check_msgs(bus)
            console.print("[green]Оба сигнала обнаружены[/]\n")
        except AssertionError as e:
            # Если assert упал, но это не ошибка остановки - выводим
            if not stop_event.is_set():
                console.print(f"[red] Assert failed: {e}[/]\n")
        except can.CanOperationError as e:
            # Игнорируем ошибки чтения при закрытии шины
            if "Bad file descriptor" in str(e) or stop_event.is_set():
                break
            console.print(f"[red]Ошибка CAN: {e}[/]\n")
        except Exception as e:
            if stop_event.is_set():
                break
            console.print(f"[red] Ошибка: {type(e).__name__}: {e}[/]\n")
        
        # Ждем либо 0.5 сек, либо сигнала остановки (мгновенная реакция на 'q')
        stop_event.wait(timeout=0.5) 


def get_can_bus():
    """Создает CAN-шину в зависимости от ОС"""
    if IS_WINDOWS:
        # Для Windows обычно используется pcan, kvaser или vector
        # Укажите здесь ваш реальный интерфейс и канал!
        # Вместо жесткого 'PCAN_USBBUS1'
        configs = can.detect_available_configs(interfaces=['pcan'])
        if configs:
            channel = configs[0]['channel'] # Автоматически возьмет PCAN_USBBUS1 (или другой, если он первый)
        else:
            raise Exception("Адаптеры PEAK не найдены")

        return can.Bus(interface='pcan', channel=channel, bitrate=500000)
        # return can.Bus(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
    else:
        # Для Linux (Orange Pi)
        return can.Bus(interface='socketcan', channel='can1', bitrate=500000)



def main(write_and_read, ui, restart_menu):
    while True:
        test_number = ui(write_and_read)
        
        if test_number == "1":
            console = Console()
            console.print("\n[green]Инициализация CAN-шины...[/]")
            
            bus = None
            # ⚠️ ВАЖНО: Создаем НОВОЕ событие для каждого запуска
            stop_event = threading.Event() 
            
            try:
                bus = get_can_bus()
                console.print("[green]Шина открыта. Тест запущен в бесконечном режиме.[/]")
                console.print("[yellow]Нажмите '4' + Enter для остановки теста[/]\n")
                
                test_thread = threading.Thread(
                    target=run_test_infinite, 
                    args=(bus, console, stop_event), 
                    daemon=True
                )
                test_thread.start()
                
                # Ждем ввода пользователя
                while not stop_event.is_set():
                    user_input = input().strip().lower()
                    if user_input == '4':
                        stop_event.set()
                        console.print("[yellow]Остановка теста...[/]")
                        break
                        
            except can.CanError as e:
                console.print(f"\n[red]Ошибка CAN: {e}[/]")
            except Exception as e:
                console.print(f"\n[red]Неожиданная ошибка: {type(e).__name__}: {e}[/]")
            finally:
                # Сначала сигнализируем потоку об остановке
                stop_event.set()
                # Даем потоку время на корректное завершение (макс 2 сек)
                test_thread.join(timeout=2.0)
                
                if bus is not None:
                    try:
                        bus.shutdown()
                    except Exception:
                        pass # Игнорируем ошибки shutdown, если шина уже мертва
                    console.print("[dim]Шина закрыта.[/]")
                    
            input("Нажмите Enter для возврата в меню...")

        elif test_number == "00":
            break
        # elif test_number == "0":
        #     pass
        else:
            print("Повторите запуск с релевантным вводом")
        
        # if restart_menu() == 1:
        #     break


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

    # table.add_column("Модуль", justify="left", style="cyan", width=10)
    # table.add_column("Состояние", style="bold", width=20)
    # table.add_column("Возможный метод исправления", width=30)
    # table.add_column("Примечание", justify="left", style="green", width=15)

    # # Пустая строка добавляется без ошибок, как вы и указали
    # table.add_row("", "", "", "") 

    # console.print(
    #     Panel(table, title="СОСТОЯНИЕ СИСТЕМЫ ТЕСТИРОВАНИЯ", border_style="white")
    # )

    instruction_text = Text()
    instruction_text.append("Для тестирования ", style="white")
    instruction_text.append("can", style="bold cyan")
    instruction_text.append(" введите ", style="white")
    instruction_text.append("1\n", style="bold cyan")
    instruction_text.append("Для выхода введите ", style="white")
    instruction_text.append("00\n", style="bold cyan")
    # instruction_text.append("Для перезапуска меню введите ", style="white")
    # instruction_text.append("0", style="bold cyan")

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