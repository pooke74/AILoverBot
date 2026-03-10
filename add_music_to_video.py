import numpy as np
import wave
import struct
import os

def generate_dark_phonk_beat(output_wav, duration=42, sample_rate=44100):
    """Karanlik, bass-agirlikli bir phonk/trap beat uretir."""
    print("Dark Phonk beat uretiliyor...")
    
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    bpm = 130
    beat_duration = 60.0 / bpm
    beat_pos = (t % beat_duration) / beat_duration  # 0-1 for each beat
    bar_pos = (t % (beat_duration * 4)) / (beat_duration * 4)  # 0-1 for each bar
    
    # === KICK DRUM (Deep 808 Sub Bass) ===
    kick_env = np.where(beat_pos < 0.15, np.exp(-beat_pos * 30), 0)
    kick_freq = 55 * np.exp(-beat_pos * 8) + 35  # Pitch drop
    kick = np.sin(2 * np.pi * kick_freq * t) * kick_env * 0.7
    
    # === HI-HAT (Metallic noise) ===
    noise = np.random.randn(total_samples) * 0.15
    half_beat = (t % (beat_duration / 2)) / (beat_duration / 2)
    hihat_env = np.where(half_beat < 0.05, np.exp(-half_beat * 80), 0)
    hihat = noise * hihat_env
    
    # === SNARE / CLAP (on beats 2 and 4) ===
    two_beat = (t % (beat_duration * 2)) / (beat_duration * 2)
    snare_trigger = np.where((two_beat > 0.48) & (two_beat < 0.55), 1.0, 0.0)
    snare_env = snare_trigger * np.exp(-(two_beat - 0.48) * 40)
    snare_noise = np.random.randn(total_samples) * 0.2
    snare = snare_noise * snare_env
    
    # === DARK PAD (Low atmospheric drone) ===
    pad = np.sin(2 * np.pi * 65 * t) * 0.08  # Low A
    pad += np.sin(2 * np.pi * 98 * t) * 0.06  # Fifth
    pad += np.sin(2 * np.pi * 130 * t) * 0.04  # Octave
    # Slow tremolo
    pad *= (1 + 0.3 * np.sin(2 * np.pi * 0.5 * t))
    
    # === MELODY (Simple dark arp) ===
    melody_notes = [130.81, 155.56, 174.61, 155.56]  # C3, Eb3, F3, Eb3 (dark minor)
    melody_beat_idx = (np.floor(t / beat_duration) % 4).astype(int)
    melody_freq = np.array([melody_notes[i] for i in melody_beat_idx])
    melody_env = np.exp(-beat_pos * 6) * 0.12
    melody = np.sin(2 * np.pi * melody_freq * t) * melody_env
    
    # === MIX ===
    mix = kick + hihat + snare + pad + melody
    
    # Soft clipping / saturation
    mix = np.tanh(mix * 1.5) * 0.8
    
    # Fade in first 2 seconds, fade out last 2 seconds
    fade_in = np.minimum(t / 2.0, 1.0)
    fade_out = np.minimum((duration - t) / 2.0, 1.0)
    mix *= fade_in * fade_out
    
    # Normalize
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val * 0.85
    
    # Convert to 16-bit PCM
    mix_int = (mix * 32767).astype(np.int16)
    
    # Write WAV
    with wave.open(output_wav, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(mix_int.tobytes())
    
    print(f"Beat kaydedildi: {output_wav}")

def merge_video_audio(video_path, audio_path, output_path):
    """Video ve audio'yu moviepy ile birlestirir."""
    print("Video ve muzik birlestiriliyor...")
    
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip
    except ImportError:
        from moviepy import VideoFileClip, AudioFileClip
    
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Trim audio to match video duration
    if audio.duration > video.duration:
        audio = audio.subclipped(0, video.duration)
    
    final = video.with_audio(audio)
    final.write_videofile(output_path, codec='libx264', audio_codec='aac', logger='bar')
    
    video.close()
    audio.close()
    print(f"Final video kaydedildi: {output_path}")

if __name__ == "__main__":
    base_dir = r"C:\Users\tolga\.gemini\antigravity\brain\fea51c54-51e5-4e4b-8654-bdd98786f35b"
    
    wav_path = os.path.join(base_dir, "dark_phonk_beat.wav")
    video_path = os.path.join(base_dir, "AILoverBot_Chat_Simulation.mp4")
    output_path = os.path.join(base_dir, "AILoverBot_Chat_Simulation_MUSIC.mp4")
    
    generate_dark_phonk_beat(wav_path, duration=42)
    merge_video_audio(video_path, wav_path, output_path)
