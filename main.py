import pyaudio
import keyboard
from pydub import AudioSegment
import os
import array

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
INPUT_DEVICE = 1
OUTPUT_DEVICE =  7
MIC_VOL = 1.0
SOUND_VOL = 0.4

# Sound mappings
key_to_sound = {
    '1': 'resources/Vine boom.mp3',
    '2': 'resources/Cat Laughing At You.mp3',
    '3': 'resources/Danger Alarm.mp3',
    '4': 'resources/Bruh Sound Effect.mp3',
    '5': 'resources/Piercing Light.mp3',
    '6': 'resources/Jingle hahal.mp3',
    '7': 'resources/Secunda.mp3',
}

# Validate sound files exist
for key, path in key_to_sound.items():
    if not os.path.exists(path):
        print(f"Warning: Sound file not found: {path}")

try:
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Set up audio streams
    micInStream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=INPUT_DEVICE
    )

    defaultOutStream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True
    )

    virtualMicOutStream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        output_device_index=OUTPUT_DEVICE
    )

    # Print device info
    mic_device_info = p.get_device_info_by_index(INPUT_DEVICE)
    virtual_mic_device_info = p.get_device_info_by_index(OUTPUT_DEVICE)
    print("========Soundboard Started========")
    print(f"[INFO] Input Device: {mic_device_info['name']}")
    print(f"[INFO] Output Device: {virtual_mic_device_info['name']}")

    # Initialize sound buffer
    soundsInStream = bytes()

    def play_sound(file):
        """Load and queue a sound file for playback."""
        try:
            # Load the sound and explicitly set the frame rate
            sound = AudioSegment.from_file(file)
            sound = sound.set_frame_rate(RATE//2)  # Force the correct sample rate
            global soundsInStream
            soundsInStream = sound.raw_data
        except Exception as e:
            print(f"Error playing sound {file}: {str(e)}")

    def mix_audio(mic_data, sound_data):
        """Mix two audio streams with ratio."""
        # Convert bytes to array of signed shorts
        mic_array = array.array('h', mic_data)
        sound_array = array.array('h', sound_data.ljust(len(mic_data), b'\x00'))
        
        # Mix the audio with 0.5 ratio for each source
        mixed = array.array('h', (
            int((m * MIC_VOL + s * SOUND_VOL))  
            for m, s in zip(mic_array, sound_array)
        ))
        
        return mixed.tobytes()

    print("Press 'q' to stop")
    running = True

    # Main loop
    while running:
        try:
            # Read from microphone
            mic_chunk = micInStream.read(CHUNK, exception_on_overflow=False)
            
            # Process sound effects
            sound_chunk = soundsInStream[:CHUNK*2]  # Get enough bytes for our frame size
            soundsInStream = soundsInStream[CHUNK*2:]
            
            # Handle keyboard input
            if keyboard.is_pressed('q'):
                running = False
            elif keyboard.is_pressed('0'):
                soundsInStream = bytes()
            else:
                for key, sound in key_to_sound.items():
                    if keyboard.is_pressed(key):
                        play_sound(sound)
                        break

            # Mix audio streams
            output_chunk = mix_audio(mic_chunk, sound_chunk)
            
            # defaultOutStream.write(output_chunk)
            virtualMicOutStream.write(output_chunk)

        except IOError as e:
            print(f"IO Error: {str(e)}")
            continue
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            break

except Exception as e:
    print(f"Fatal error: {str(e)}")

finally:
    # Cleanup
    print("========Soundboard Stopped========")
    try:
        keyboard.unhook_all()
        micInStream.stop_stream()
        defaultOutStream.stop_stream()
        virtualMicOutStream.stop_stream()
        micInStream.close()
        defaultOutStream.close()
        virtualMicOutStream.close()
        p.terminate()
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")