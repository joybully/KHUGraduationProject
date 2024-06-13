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

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sine Wave Generator")

# Load image
image = pygame.image.load("asphalt.jpg")
image = pygame.transform.scale(image, (800, 600))
image_array = pygame.surfarray.array3d(image)

# Variables for tracking mouse movement
last_time = time.time()
last_pos = pygame.mouse.get_pos()

# Function to get frequency and amplitude based on pixel color
def get_frequency_amplitude(x, y):
    r, g, b = image_array[x, y]
    frequency = 10 + ((r+g+b) / 765.0) * 400  # Map red component to frequency range
    amplitude = (g / 255.0) * 0.5 + 0.5  # Map green component to amplitude range
    return frequency, amplitude

# Audio callback function
def callback(in_data, frame_count, time_info, status):
    global frequency, amplitude, last_time, last_pos

    # Get current mouse position
    current_pos = pygame.mouse.get_pos()
    x, y = current_pos

    # Get frequency and amplitude based on pixel color
    frequency, amplitude = get_frequency_amplitude(x % 800, y % 600)

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

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Draw image
    screen.blit(image, (0, 0))
    pygame.display.flip()

# Clean up
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
