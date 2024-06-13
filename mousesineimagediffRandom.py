import numpy as np
import pyaudio
import pygame
import time

# Constants
SAMPLE_RATE = 44100  # Sample rate in Hz
BUFFER_SIZE = 256   # Buffer size for audio stream
BASE_AMPLITUDE = 0.5 # Base amplitude of the sine wave

# Initialize PyAudio
p = pyaudio.PyAudio()

# Global variables
frequency = 440.0  # Initial frequency in Hz (A4 note)
amplitude = BASE_AMPLITUDE  # Initial amplitude
running = True

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1200, 600))
pygame.display.set_caption("Sine Wave Generator")

# Load image
image = pygame.image.load("asphaltHalf2.png")  # Replace "asphalt.jpg" with the actual image path
image = pygame.transform.scale(image, (1200, 600))
image_array = pygame.surfarray.array3d(image)

# Variables for tracking mouse movement
last_time = time.time()
last_pos = pygame.mouse.get_pos()

# Function to get frequency based on pixel color
def get_frequency(x, y):
    r, g, b = image_array[x % 1200, y % 600]  # Ensure x, y are within bounds
    frequency = 50 + ((r + g + b) / 765.0) * 100  # Map RGB components to frequency range 50 - 150 Hz
    return min(frequency, 150)  # Cap the frequency to a maximum of 150 Hz

# Function to get the noise amplitude based on the RGB difference
def get_noise_amplitude(last_pos, current_pos):
    r1, g1, b1 = image_array[last_pos[0] % 1200, last_pos[1] % 600]
    r2, g2, b2 = image_array[current_pos[0] % 1200, current_pos[1] % 600]
    print(current_pos)
    rgb_diff = np.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) / 441.67  # Normalize the difference
    return rgb_diff

# Audio callback function
def callback(in_data, frame_count, time_info, status):
    global frequency, amplitude, noise_amplitude
    t = (np.arange(frame_count) + callback.t_offset) / SAMPLE_RATE
    
    # Generate base sine wave
    sine_wave = np.sin(2 * np.pi * frequency * t)
    
    # Add noise based on the RGB difference
    noise = np.random.normal(noise_amplitude-0.1, noise_amplitude, frame_count)
    
    # Combine sine wave and noise
    data = (amplitude * (sine_wave + noise)).astype(np.float32)
    #data = (amplitude * sine_wave).astype(np.float32)
    
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
        x, y = current_pos
        frequency = get_frequency(x, y)

        # Adjust amplitude based on mouse speed
        amplitude = min(speed / 500.0, 1.0)  # Normalize speed to a reasonable amplitude range
        
        # Get noise amplitude based on RGB difference
        noise_amplitude = get_noise_amplitude(last_pos, current_pos)

        # Update last position and time
        last_time = current_time
        last_pos = current_pos

        # Draw image
        screen.blit(image, (0, 0))
        pygame.display.flip()

        # Limit the update rate to reduce CPU usage
        time.sleep(0.01)
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()
