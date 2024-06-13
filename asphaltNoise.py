import numpy as np
import sounddevice as sd
from PIL import Image, ImageTk
import tkinter as tk

def generate_scratch_sound(intensity, duration=0.1, sample_rate=44100):
    frequency = 1000 + (intensity * 1000)  # Map intensity to frequency
    noise_level = intensity * 0.5  # Map intensity to noise level
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = np.sin(2 * np.pi * frequency * t)
    
    # Adding noise
    noise = np.random.normal(0, noise_level, signal.shape)
    scratch_sound = signal + noise

    # Normalize the sound to prevent clipping
    scratch_sound = scratch_sound / np.max(np.abs(scratch_sound))
    
    return scratch_sound

def play_scratch_sound(intensity):
    print(f"Playing sound with intensity: {intensity}")  # Debug statement
    sound = generate_scratch_sound(intensity)
    sd.play(sound, 44100)
    sd.wait()  # Wait until sound finishes playing

def get_intensity_from_image(image, x, y):
    # Ensure the coordinates are within the image bounds
    if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
        intensity = image[y, x] / 255.0  # Normalize intensity to [0, 1]
        print(f"Pixel intensity at ({x}, {y}): {intensity}")  # Debug statement
        return intensity
    return 0

def on_mouse_move(event):
    x, y = event.x, event.y
    intensity = get_intensity_from_image(image_array, x, y)
    play_scratch_sound(intensity)

# Load the image using PIL and convert to grayscale
image_path = 'asphalt.jpg'
image = Image.open(image_path).convert('L')
image_array = np.array(image)

# Create a Tkinter window to display the image and track the mouse
root = tk.Tk()
root.title("Asphalt Scratch Sound Simulator")
tk_image = ImageTk.PhotoImage(image=image)

label = tk.Label(root, image=tk_image)
label.pack()

label.bind('<Motion>', on_mouse_move)

root.mainloop()
