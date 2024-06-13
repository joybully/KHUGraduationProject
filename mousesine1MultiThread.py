import numpy as np
import pyaudio
import pygame
import time
import threading

# Constants
SAMPLE_RATE = 44100  # Sample rate in Hz
BUFFER_SIZE = 1024   # Buffer size for audio stream
AMPLITUDE = 0.5      # Amplitude of the sine wave

# Initialize PyAudio
p = pyaudio.PyAudio()

# Global variables
frequency = 440.0  # Initial frequency in Hz (A4 note)
amplitude = AMPLITUDE  # Initial amplitude

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sine Wave Generator")

# Variables for tracking mouse movement
last_time = time.time()
last_pos = pygame.mouse.get_pos()

# Audio callback function
def callback(in_data, frame_count, time_info, status):
    global frequency, amplitude, last_time, last_pos

    # Get current mouse position
    current_pos = pygame.mouse.get_pos()

    # Calculate mouse speed
    current_time = time.time()
    delta_time = current_time - last_time
    delta_pos = ((current_pos[0] - last_pos[0]) ** 2 + (current_pos[1] - last_pos[1]) ** 2) ** 0.5
    speed = delta_pos / delta_time if delta_time > 0 else 0

    # Adjust frequency based on mouse speed
    frequency = 2.0 + (speed / 2000.0) * (200.0 - 2.0)  # Frequency range from 2 Hz to 200 Hz
    if frequency > 700:
        frequency = 700

    # Adjust amplitude based on frequency
    amplitude = frequency / 400 + 0.5
    if amplitude > 1:
        amplitude = 1

    # Update last position and time
    last_time = current_time
    last_pos = current_pos

    # Generate sine wave data
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

# Thread function for Pygame main loop
def pygame_loop():
    global running
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw background image or fill screen with color (optional)
        screen.fill((0, 0, 0))
        pygame.display.flip()

# Create and start the Pygame thread
running = True
pygame_thread = threading.Thread(target=pygame_loop)
pygame_thread.start()

# Main thread: keep the audio stream running
try:
    while running:
        time.sleep(0.1)  # Keep the main thread alive
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()
    pygame_thread.join()
