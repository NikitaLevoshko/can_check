from time import time

def test_can_check_msgs(bus_binar):
    timeout = 1.0
    silence_timeout = 0.3  # Если тишина > 0.3с — считаем, что устройство выключилось
    
    start_time = time()
    last_msg_time = start_time
    
    found_ids = set()  # Используем set для быстрого поиска
    hmi_seen_in_cycle = False
    car_seen_in_cycle = False
    
    while time() - start_time < timeout:
        msg = bus_binar.recv(timeout=0.01)  # Уменьшил recv-таймаут для更快的 реакции
        
        if msg is not None:
            last_msg_time = time()
            can_id = msg.arbitration_id
            
            if can_id == 0x10FF0181:
                hmi_seen_in_cycle = True
                found_ids.add(can_id)
            elif can_id == 0x18FF0580:
                car_seen_in_cycle = True
                found_ids.add(can_id)
                
            # Оба сообщения получены в текущем цикле — успех
            if hmi_seen_in_cycle and car_seen_in_cycle:
                print("✅ Оба сообщения обнаружены!")
                return  # Успешный выход
                
        else:
            # Проверяем "тишину" на шине
            if time() - last_msg_time > silence_timeout:
                # print(f"️ Тишина на шине {silence_timeout}s. Сигнал пропал.")
                break  # Выходим из цикла, чтобы assert ниже сработал
    
    # Если вышли по таймауту или тишине — проверяем флаги
    if hmi_seen_in_cycle:
        assert car_seen_in_cycle, f"Control (0x18FF0580) не обнаружен"
    elif car_seen_in_cycle:
        assert hmi_seen_in_cycle, f"HMI (0x10FF0181) не обнаружен"
    else:
        assert hmi_seen_in_cycle+car_seen_in_cycle==True, f"Оба сигнала не обнаружены"