#Clock with neopixels

#Get functions from external sources
import astral.geocoder
import astral.location
import astral.sun
import copy
import datetime
import numpy as np
import time

from hex2rgb import hex2rgb, rgb2hex
import led_driver_neopixel as led



def get_auto_brightness(date, max_brightness=1.0, min_brightness=0.0):
    """
    Get the brightness value based on the time of day

    Args:
        date (datetime.datetime): The current time to check
        max_brightness (float): The maximum brightness (at the peak of the day)
        min_brightness (float): The minimum brightness (at night)
    
    Returns:
        brightness (float): The brightness value
    """
    # Get the sunrise/sunset data calculator:
    city = astral.geocoder.lookup("Boston", astral.geocoder.database())
    boston = astral.location.Location(city)
    sun_events = astral.sun.sun(city.observer, date=date, tzinfo=boston.timezone)

    # Compute the dawn and dusk ratios
    dawn_ratio = (sun_events['dawn'].hour*60 + sun_events['dawn'].minute)/(60*24)
    dusk_ratio = (sun_events['dusk'].hour*60 + sun_events['dusk'].minute)/(60*24)
    
    now_ratio = ((date.hour*60.0)+date.minute)/(60*24)
    
    
    if (now_ratio <= dawn_ratio) or (now_ratio >= dusk_ratio):
        brightness =  min_brightness
    else:
        middle = (dawn_ratio + dusk_ratio)/2
        span = dusk_ratio - dawn_ratio
        if now_ratio < middle:
            brightness = min_brightness + (max_brightness - min_brightness)*(now_ratio-dawn_ratio)/(span*0.5)
        else:
            brightness = min_brightness + (max_brightness - min_brightness)*(dusk_ratio-now_ratio)/(span*0.5)
            
    return brightness 
        

if __name__ == "__main__":
    #Define some low-level pin variables
    pin_config = [
        {'pin': 10, 'num_pixels': 9, 'start_idx': 0},
        {'pin': 10, 'num_pixels': 15, 'start_idx': 9},
        {'pin': 21, 'num_pixels': 9, 'start_idx': 0},
        {'pin': 21, 'num_pixels': 15, 'start_idx': 9},
    ]

    led_handler = led.PixelHandler(pin_config)

    duration = 20.0 # [sec]
    time_start = datetime.datetime.now()
    now = datetime.datetime.now()

    color_check_time = 60.0 #[sec]
    last_color_check = time_start-datetime.timedelta(seconds=color_check_time+1)

    week_colors =[
        [255, 150, 0], # Monday
        [255, 60, 0], # Tuesday
        [255, 10, 0], # Wednesday
        [130, 0, 255], # Thursday
        [0, 50, 255], # Friday
        [0, 255, 40], # Saturday
        [100, 255, 0], # Sunday
    ]

    main_color = [255,255,255]
    main_brightness = 100

    indicator_hr = led.Indicator(
        pin_config[0]['num_pixels'],
    )

    indicator_min = led.Indicator(
        pin_config[1]['num_pixels'],
        2,
        pin_config[1]['num_pixels']-2,
    )

    indicator_sec = led.Indicator(
        pin_config[3]['num_pixels'],
        2,
        pin_config[3]['num_pixels']-2,
    )

    indicator_full = led.Indicator(
        pin_config[2]['num_pixels'],
    )

    indicator_hr.buffer_color = main_color
    indicator_min.buffer_color = [0,0,0]
    indicator_sec.buffer_color = [0,0,0]

    indicator_full.buffer_color = main_color

    while True:
        try:
            now = datetime.datetime.now()
            
            # Update the color if the weekday changes
            if (now - last_color_check).total_seconds() >= color_check_time:
                weekday = int(now.weekday())
                main_color = week_colors[weekday]
            
                main_brightness = get_auto_brightness(now, 80, 5)
                            
                indicator_hr.brightness = main_brightness +5
                indicator_min.brightness = main_brightness
                indicator_sec.brightness = main_brightness
                indicator_full.brightness = main_brightness+5

                last_color_check = copy.deepcopy(now)
            
            color_array_hr = indicator_hr.compute_fractional_colors(
                main_color,
                [0,0,0],
                (now.hour+1)/24.0,
            )
            
            color_array_min = indicator_min.compute_fractional_colors(
                main_color,
                [0,0,0],
                (now.minute+1)/60.0,
            )
            
            color_array_sec = indicator_sec.compute_fractional_colors(
                main_color,
                [0,0,0],
                (((now.second)*1e6)+now.microsecond)/60e6,
            )

            color_array_static = indicator_full.compute_fractional_colors(
                main_color,
                main_color,
                0,
            )
            
            led_handler.set_color_array(0, color_array_hr, invert=False)
            led_handler.set_color_array(1, color_array_min, invert=True)
            led_handler.set_color_array(3, color_array_sec, invert=True)

            led_handler.set_color_array(2, color_array_static, invert=False)
            
            time.sleep(0.1)
    
        except KeyboardInterrupt:
            print("\nStopping...")
            break

