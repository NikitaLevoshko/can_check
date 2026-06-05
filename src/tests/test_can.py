from time import time


def test_can_check_msgs(bus_binar):
    # 10FF0181 hmi
    # 10FF0080 18FF0580 18FF0480 18FF0380 18FF0280 18FE6D80 18EA4480 72C control
    hmi_flag = False
    car_flag = False
    timeout = 10.0  # секунды
    start_time = time()
    found_ids = []
    while time() - start_time < timeout:
        # Читаем CAN сообщение
        msg = bus_binar.recv(timeout=0.1)  # Замените на ваш метод
        if msg is not None:
            can_id = msg.arbitration_id
            if can_id not in found_ids:
                found_ids.append(can_id)
                if can_id == 0x10FF0181:
                # if can_id == 850:
                    hmi_flag = True
                if can_id == 0x18FF0580:
                # if can_id == 850:
                    car_flag = True
        if hmi_flag and car_flag:
            print("Оба сообщения обнаружены!")
            break

    assert hmi_flag, f"hmi_flag == {hmi_flag}"
    assert car_flag, f"car_flag == {car_flag}"