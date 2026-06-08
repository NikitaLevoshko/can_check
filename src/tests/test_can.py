from time import time, sleep

def test_can_check_msgs(bus_binar):
    timeout = 1.0
    silence_timeout = 0.2
    poll_interval = 0.01
    
    _flush_bus_buffer(bus_binar)
    
    start_time = time()
    last_msg_time = start_time
    
    hmi_ok = False
    car_ok = False
    
    while time() - start_time < timeout:
        msg = bus_binar.recv(timeout=0.0)
        
        if msg is not None:
            last_msg_time = time()
            aid = msg.arbitration_id
            
            if aid == 0x10FF0181: 
                hmi_ok = True
            if aid == 0x18FF0580: 
                car_ok = True
                
            if hmi_ok and car_ok:
                return
        else:
            if time() - last_msg_time > silence_timeout:
                break
        
        sleep(poll_interval)
    
    if hmi_ok:
        assert car_ok, f"Control (0x18FF0580) не обнаружен"
    elif car_ok:
        assert hmi_ok, f"HMI (0x10FF0181) не обнаружен"
    else:
        assert hmi_ok+car_ok==True, f"Оба сигнала не обнаружены"


def _flush_bus_buffer(bus, max_flush_time=0.1):
    flush_start = time()
    flushed_count = 0
    while time() - flush_start < max_flush_time:
        msg = bus.recv(timeout=0.0)
        if msg is None:
            break  # Буфер пуст
        flushed_count += 1
    
    if flushed_count > 0:
        # print(f"[DEBUG] Сброшено {flushed_count} старых сообщений из буфера")
        pass