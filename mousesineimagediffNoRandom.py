import numpy as np
import pyaudio
import pygame
import time

# Constants
SAMPLE_RATE = 44100  # Sample rate in Hz
BUFFER_SIZE = 512    # Buffer size for audio stream (reduced for lower latency)
BASE_AMPLITUDE = 0.1 # Base amplitude of the sine wave

# Initialize PyAudio
p = pyaudio.PyAudio()

# Global variables
frequency = 440.0  # Initial frequency in Hz (A4 note)
amplitude = BASE_AMPLITUDE  # Initial amplitude
running = True

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sine Wave Generator")

# Load image
image = pygame.image.load("asphalt.jpg")  # Replace "asphalt.jpg" with the actual image path
image = pygame.transform.scale(image, (800, 600))
image_array = pygame.surfarray.array3d(image)

# Variables for tracking mouse movement and color
last_time = time.time()
last_pos = pygame.mouse.get_pos()
last_rgb = image_array[last_pos[0] % 800, last_pos[1] % 600]

# Function to get frequency based on pixel color
def get_frequency(x, y):
    r, g, b = image_array[x % 800, y % 600]  # Ensure x, y are within bounds
    frequency = 50 + ((r + g + b) / 765.0) * 300  # Map RGB components to frequency range 50 - 150 Hz
    return min(frequency, 150)  # Cap the frequency to a maximum of 150 Hz

# Audio callback function
def callback(in_data, frame_count, time_info, status):
    global frequency, amplitude
    t = (np.arange(frame_count) + callback.t_offset) / SAMPLE_RATE
    
    # Calculate RGB difference between current and last position
    current_pos = pygame.mouse.get_pos()
    x, y = current_pos
    current_rgb = image_array[x % 800, y % 600]
    #rgb_diff = np.sqrt(np.sum((current_rgb - last_rgb) ** 2)) / 255.0  # Normalize the RGB difference
    rgb_diff = np.sum(current_rgb - last_rgb) / 255.0  # Normalize the RGB difference
    
    # Calculate mouse speed
    current_time = time.time()
    delta_time = current_time - last_time
    delta_pos = ((current_pos[0] - last_pos[0]) ** 2 + (current_pos[1] - last_pos[1]) ** 2) ** 0.5
    speed = delta_pos / delta_time if delta_time > 0 else 0

    # Adjust amplitude based on RGB difference
    #amplitude = BASE_AMPLITUDE + 0.9 * rgb_diff * min(speed / 200.0, 1.0)  # Adjust amplitude based on RGB difference
    amplitude = BASE_AMPLITUDE + 0.9 * min(speed / 100.0, 1.0)  # Adjust amplitude based on RGB difference
    if amplitude > 1:
        amplitude = 1
    # Generate sine wave
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
    
    callback.t_offset += frame_count
    last_rgb[:] = current_rgb  # Update last RGB value
    return (sine_wave.astype(np.float32).tobytes(), pyaudio.paContinue)

callback.t_offset = 0

# Open audio stream
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=SAMPLE_RATE,
                output=True,
                frames_per_buffer=BUFFER_SIZE,
                stream_callback=callback)
stream.start_stream()

# Main Pygame loop
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get current mouse position
        current_pos = pygame.mouse.get_pos()
        current_time = time.time()
        
        # Calculate mouse speed
        delta_time = current_time - last_time
        delta_pos = ((current_pos[0] - last_pos[0]) ** 2 + (current_pos[1] - last_pos[1]) ** 2) ** 0.5
        speed = delta_pos / delta_time if delta_time > 0 else 0

        # Get frequency based on pixel color
        frequency = get_frequency(current_pos[0], current_pos[1])

        # Update last position and time
        last_time = current_time
        last_pos = current_pos

        # Draw image
        screen.blit(image, (0, 0))
        pygame.display.flip()

        # Limit the update rate to reduce CPU usage
        pygame.time.Clock().tick(60)  # Cap frame rate to 60 FPS
        
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()
