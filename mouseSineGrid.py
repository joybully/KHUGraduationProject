import numpy as np
import pyaudio
import pygame
import time

# Constants
SAMPLE_RATE = 44100  # Sample rate in Hz
BUFFER_SIZE = 1024   # Buffer size for audio stream
AMPLITUDE = 0.5      # Amplitude of the sine wave

# Initialize PyAudio
p = pyaudio.PyAudio()

# Global variables
frequency = 440.0  # Initial frequency in Hz (A4 note)
amplitude = AMPLITUDE  # Initial amplitude

# Audio callback function
def callback(in_data, frame_count, time_info, status):
    global frequency, amplitude
    t = (np.arange(frame_count) + callback.t_offset) / SAMPLE_RATE
    data = (amplitude * np.sin(2 * np.pi * frequency * t)).astype(np.float32)
    callback.t_offset += frame_count
    return (data.tobytes(), pyaudio.paContinue)

callback.t_offset = 0

# Open audio stream
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLE_RATE,
                output=True,
                frames_per_buffer=BUFFER_SIZE,
                stream_callback=callback)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
bg = pygame.image.load("C:/Users/Baptist/Downloads/mousePyPro/gridMouse2.jpg")
bg = pygame.transform.scale(bg,(800, 600))
pygame.display.set_caption("Sine Wave Generator")

# Variables for tracking mouse movement
last_time = time.time()
last_pos = pygame.mouse.get_pos()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    current_time = time.time()
    current_pos = pygame.mouse.get_pos()
    
    # Adjust frequency based on mouse positiond
    if (current_pos[0]%134<=7 or current_pos[0]%134>=127 or current_pos[1]%120<=7 or current_pos[1]%120>=113):
        frequency = 200
        amplitude = 1.0
    else:
        frequency = 0
        amplitude = 0.0
    screen.blit(bg, (0, 0))
    pygame.display.flip()

    time.sleep(0.001)  # Reduce CPU usage

# Clean up
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
