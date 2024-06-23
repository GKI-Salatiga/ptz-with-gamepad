# -*- coding: utf-8 -*-
# 
# Control the VISCA PTZ camera using a standard (non-XBox) gamepad
# By Samarthya Lykamanuella (groaking)
# Licensed under GPL-3.0
# 
# For Microntek USB Joystick types
# ---
# Gamepad event listener using Python
# -> SOURCE: https://github.com/zeth/inputs/blob/master/examples/gamepad_example.py
# Multithreading tips for gamepads
# -> SOURCE: https://gist.github.com/effedebe/6cae2a5849923fb373ab749594b9ed50

# SOURCE: https://www.pygame.org/docs/ref/joystick.html
import pygame
pygame.init()

from pyviscas import visca
from threading import Thread
from tkinter import messagebox
from tkinter.simpledialog import askstring
import numpy
import sys
import time

class GPad(Thread):
    ''' This class listens to the gamepad event without blocking the main code (using multithreading). '''
    
    def __init__(self):
        Thread.__init__(self)
        self.ABS_HAT0 = (0, 0)
        self.ABS_JOY_R_Y = 128
        self.ABS_JOY_L_X = 128
        self.ABS_JOY_L_Y = 128
        self.ABS_JOY_R_X = 128
        self.BTN_JOY_L = 0
        self.BTN_JOY_R = 0
        self.CIRCLE = 0
        self.CROSS = 0
        self.L1 = 0
        self.L2 = 0
        self.MENU = 0
        self.R1 = 0
        self.R2 = 0
        self.SQUARE = 0
        self.START = 0
        self.TRIANGLE = 0
    
    def run(self):

        # This dict can be left as-is, since pygame will generate a
        # pygame.JOYDEVICEADDED event for every joystick connected
        # at the start of the program.
        joysticks = {}
    
        try:
            while True:
                # Event processing step.
                # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
                # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
                for event in pygame.event.get():
                    # Handle hotplugging
                    if event.type == pygame.JOYDEVICEADDED:
                        # This event will be generated when the program starts for every
                        # joystick, filling up the list without needing to create them manually.
                        joy = pygame.joystick.Joystick(event.device_index)
                        joysticks[joy.get_instance_id()] = joy
                        print(f"Joystick {joy.get_instance_id()} connected.")
                
                for joystick in joysticks.values():
                    # Category of binary respond values
                    self.L1 = joystick.get_button(4)
                    self.L2 = joystick.get_button(6)
                    self.R1 = joystick.get_button(5)
                    self.R2 = joystick.get_button(7)
                    self.MENU = joystick.get_button(8)
                    self.START = joystick.get_button(9)
                    self.BTN_JOY_L = joystick.get_button(10)
                    self.BTN_JOY_R = joystick.get_button(11)
                    self.CIRCLE = joystick.get_button(1)
                    self.CROSS = joystick.get_button(2)
                    self.SQUARE = joystick.get_button(3)
                    self.TRIANGLE = joystick.get_button(0)
                    
                    # Category of analog values
                    self.ABS_HAT0 = joystick.get_hat(0)
                    self.ABS_JOY_L_X = float( str(f"{ ('%.3f' % joystick.get_axis(0)) }") )
                    self.ABS_JOY_L_Y = float( str(f"{ ('%.3f' % joystick.get_axis(1)) }") )
                    self.ABS_JOY_R_X = float( str(f"{ ('%.3f' % joystick.get_axis(2)) }") )
                    self.ABS_JOY_R_Y = float( str(f"{ ('%.3f' % joystick.get_axis(3)) }") )
        except Exception as e:
            messagebox.showerror('Unknown gamepad error', f'Unknown error is detected. Please check your gamepad console connection: {e}')
            sys.exit()

def get_chunk(val, min_chunk, max_chunk):
    '''
    Calculate the absolute PTZ chunk according to the analog joystick's input voltage.
    If val == 0.004, then the joystick is at rest.
    The range of value (val) is within -1 and 1.
    '''
    i = numpy.abs( val )
    return float( ( ( max_chunk - min_chunk) * float(i) ) + min_chunk )

def get_speed(val, max_speed):
    '''
    Calculate the absolute speed according to the analog joystick's input voltage.
    If val == 0.004, then the joystick is at rest.
    The range of value (val) is within -1 and 1.
    '''
    i = numpy.abs( val )
    return float( max_speed * float(i) )

def main(port='/dev/ttyUSB0'):
    ''' Actually controls the VISCA PTZ camera using joystick/gamepad. '''
    
    # Establish the non-blocking multithreading for analog input
    game_pad = GPad()
    game_pad.start()
    
    # Establish and initialize the VISCA object
    # (Change the port value according to your system's availability.)
    cam = visca.PTZ(port)
    
    # Set the max speed (pixel per 100 ms) of the X-Y joystick movement
    MAX_MOVEMENT_SPEED = 4
    
    # The maximum chunks of movement per pan-tilt relative movement
    MIN_PT_CHUNK = 5
    MAX_PT_CHUNK = 10
    
    # The maximum chunks of movement per zoom relative movement
    MAX_ZOOM_CHUNK = 200
    
    # Set the delay time for movement speed
    MOVEMENT_REDUNDANT_DELAY = 0.05
    
    # Set the delay time after each movement, before stopping any continuous command
    MOVEMENT_STOP_DELAY = 0.05
    MOVEMENT_STOP_DELAY_LONG = 0.5
    
    # If val == 0.004, then the joystick is at rest.
    JOYSTICK_REST_VAL = 0.004
    JOYSTICK_MIN_VAL = -1
    JOYSTICK_MAX_VAL = 1
    
    # Fail-safe error catching with infinite loop
    while True:
        
        # Recalling presets: left hand
        if game_pad.ABS_HAT0 == (0, 1) and game_pad.MENU == 0:
            cam.preset_recall(4)
            game_pad.ABS_HAT0 = (0, 0)  # --- blocking
        if game_pad.ABS_HAT0 == (1, 0) and game_pad.MENU == 0:
            cam.preset_recall(5)
            game_pad.ABS_HAT0 = (0, 0)  # --- blocking
        if game_pad.ABS_HAT0 == (0, -1) and game_pad.MENU == 0:
            cam.preset_recall(6)
            game_pad.ABS_HAT0 = (0, 0)  # --- blocking
        if game_pad.ABS_HAT0 == (-1, 0) and game_pad.MENU == 0:
            cam.preset_recall(7)
            game_pad.ABS_HAT0 = (0, 0)  # --- blocking
        
        # Recalling presets: right hand
        if game_pad.TRIANGLE == 1 and game_pad.MENU == 0:
            cam.preset_recall(0)
            game_pad.TRIANGLE = 0  # --- blocking
        if game_pad.CIRCLE == 1 and game_pad.MENU == 0:
            cam.preset_recall(1)
            game_pad.CIRCLE = 0  # --- blocking
        if game_pad.CROSS == 1 and game_pad.MENU == 0:
            cam.preset_recall(2)
            game_pad.CROSS = 0  # --- blocking
        if game_pad.SQUARE == 1 and game_pad.MENU == 0:
            cam.preset_recall(3)
            game_pad.SQUARE = 0  # --- blocking
        
        # Setting/assigning presets: left hand
        if game_pad.ABS_HAT0 == (0, 1) and game_pad.MENU == 1:
            cam.preset_set(4)
            game_pad.ABS_HAT0 = (0, 0)  # --- blocking
        if game_pad.ABS_HAT0 == (1, 0) and game_pad.MENU == 1:
            cam.preset_set(5)
            game_pad.ABS_HAT0 = (0, 0)  # --- blocking
        if game_pad.ABS_HAT0 == (0, -1) and game_pad.MENU == 1:
            cam.preset_set(6)
            game_pad.ABS_HAT0 = (0, 0)  # --- blocking
        if game_pad.ABS_HAT0 == (-1, 0) and game_pad.MENU == 1:
            cam.preset_set(7)
            game_pad.ABS_HAT0 = (0, 0)  # --- blocking
        
        # Setting/assigning presets: right hand
        if game_pad.TRIANGLE == 1 and game_pad.MENU == 1:
            cam.preset_set(0)
            game_pad.TRIANGLE = 0  # --- blocking
        if game_pad.CIRCLE == 1 and game_pad.MENU == 1:
            cam.preset_set(1)
            game_pad.CIRCLE = 0  # --- blocking
        if game_pad.CROSS == 1 and game_pad.MENU == 1:
            cam.preset_set(2)
            game_pad.CROSS = 0  # --- blocking
        if game_pad.SQUARE == 1 and game_pad.MENU == 1:
            cam.preset_set(3)
            game_pad.SQUARE = 0  # --- blocking
        
        # Adjusting iris
        if game_pad.L1 == 1 and game_pad.MENU == 0:
            cam.iris_up()
        if game_pad.L2 == 1 and game_pad.MENU == 0:
            cam.iris_down()
        
        # Adjusting brightness
        if game_pad.R1 == 1 and game_pad.MENU == 0:
            cam.bright_up()
        if game_pad.R2 == 1 and game_pad.MENU == 0:
            cam.bright_down()
        
        # Adjusting gain
        if game_pad.L1 == 1 and game_pad.MENU == 1:
            cam.gain_up()
        if game_pad.L2 == 1 and game_pad.MENU == 1:
            cam.gain_down()
        
        # Adjusting aperture
        if game_pad.R1 == 1 and game_pad.MENU == 1:
            cam.aperture_up()
        if game_pad.R2 == 1 and game_pad.MENU == 1:
            cam.aperture_down()
        
        # Movement actions (left-right panning)
        if game_pad.ABS_JOY_L_X != JOYSTICK_REST_VAL:
            val = game_pad.ABS_JOY_L_X
            i = round( get_speed(val, MAX_MOVEMENT_SPEED) )
            j = round( get_chunk(val, MIN_PT_CHUNK, MAX_PT_CHUNK) )
            # Do the movement
            if val >= JOYSTICK_MIN_VAL and val < JOYSTICK_REST_VAL:
                cam.set_pan_rel(-j, i)  # --- left
                time.sleep(MOVEMENT_STOP_DELAY)
            elif val > JOYSTICK_REST_VAL and val <= JOYSTICK_MAX_VAL:
                cam.set_pan_rel(j, i)  # --- right
                time.sleep(MOVEMENT_STOP_DELAY)
        
        # Movement actions (up-down tilting)
        if game_pad.ABS_JOY_L_Y != 128:
            val = game_pad.ABS_JOY_L_Y
            i = round( get_speed(val, MAX_MOVEMENT_SPEED) )
            j = round( get_chunk(val, MIN_PT_CHUNK, MAX_PT_CHUNK) )
            # Do the movement
            if val >= JOYSTICK_MIN_VAL and val < JOYSTICK_REST_VAL:
                cam.set_tilt_rel(j, i)  # --- up
                time.sleep(MOVEMENT_STOP_DELAY)
            elif val > JOYSTICK_REST_VAL and val <= JOYSTICK_MAX_VAL:
                cam.set_tilt_rel(-j, i)  # --- down
                time.sleep(MOVEMENT_STOP_DELAY)
        
        # Movement actions (zoom)
        if game_pad.ABS_JOY_R_Y != 128:
            val = game_pad.ABS_JOY_R_Y
            i = get_speed(val, MAX_ZOOM_CHUNK)
            # Do the movement
            if val >= JOYSTICK_MIN_VAL and val < JOYSTICK_REST_VAL:
                cam.set_zoom_rel(round(i))  # --- zoom in
                time.sleep(MOVEMENT_STOP_DELAY)
            elif val > JOYSTICK_REST_VAL and val <= JOYSTICK_MAX_VAL:
                cam.set_zoom_rel(0 - round(i))  # --- zoom out
                time.sleep(MOVEMENT_STOP_DELAY)
        
        # Movement actions (focus)
        """
        if game_pad.ABS_JOY_R_X != 128:
            val = game_pad.ABS_JOY_R_X
            i = get_speed(val, MAX_MOVEMENT_SPEED)
            # Do the movement
            if val >= JOYSTICK_MIN_VAL and val < JOYSTICK_REST_VAL:
                cam.focus_near(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.focus_stop()
            elif val > JOYSTICK_REST_VAL and val <= JOYSTICK_MAX_VAL:
                cam.focus_far(round(i))
                time.sleep(MOVEMENT_STOP_DELAY)
                cam.focus_stop()
        """
        
        # Analog center button press actions
        # ---
        # Move camera to home/default position
        if game_pad.BTN_JOY_L == 1:
            cam.home()
            game_pad.BTN_JOY_L = 0  # --- blocking
        # Perform autofocus
        if game_pad.BTN_JOY_R == 1:
            cam.autofocus_sens_low()
            game_pad.BTN_JOY_R = 0  # --- blocking
        
        # Prevent too fast a movement
        time.sleep(MOVEMENT_REDUNDANT_DELAY)
    
    # Wait until the end of the game_pad thread
    game_pad.joint()
    
if __name__ == "__main__":
    # Prompt for the PTZ's USB serial port
    port = askstring(
        'Serial USB Input',
        'Please enter the VISCA PTZ\'s registered serial port\ne.g. Windows: "COM1", "COM2", etc.\ne.g. Linux: "/dev/ttyUSB0", "/dev/ttyUSB1", etc.'
    )
    
    main(port)
