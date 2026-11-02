import soundcard as sc

monitor = sc.get_microphone(id=f"{sc.default_speaker().id}.monitor", include_loopback=True)

with monitor.recorder(samplerate=48000, channels=2, blocksize=1024) as stream:
    while True:
        audio = stream.record(numframes=1024)
        print(f"RMS: {(audio**2).mean() ** 0.5:.4f}")
