import os
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment

st.set_page_config(page_title="Audio Trimmer & Player", layout="wide")
st.title("🎵 Audio Trimmer & Player")

# 1. File Upload
uploaded_file = st.sidebar.file_uploader(
    "Upload an Audio File", 
    type=["mp3", "wav", "ogg", "flac", "m4a"]
)

if uploaded_file is not None:
    # Load audio data using Pydub
    # We read from the file pointer directly
    audio = AudioSegment.from_file(uploaded_file)
    duration_sec = len(audio) / 1000.0
    
    st.sidebar.success(f"Loaded: {uploaded_file.name}")
    st.sidebar.info(f"Total Duration: {duration_sec:.2f} seconds")

    # 2. Trim Controls (Sliders)
    st.subheader("✂️ Trim Controls")
    col1, col2 = st.columns(2)
    with col1:
        start_val = st.slider("Start Position (s)", 0.0, duration_sec, 0.0, step=0.1)
    with col2:
        end_val = st.slider("End Position (s)", 0.0, duration_sec, duration_sec, step=0.1)
        
    if start_val >= end_val:
        st.error("Error: Start position must be less than the end position.")
    else:
        # 3. Waveform Generation
        st.subheader("📊 Waveform Visualizer")
        
        # Downsample audio data for fast plotting
        samples = np.array(audio.get_array_of_samples())
        if audio.channels == 2:
            samples = samples[::2]  # Take left channel

        step = max(1, len(samples) // 1000)
        downsampled = samples[::step]
        time_axis = np.linspace(0, duration_sec, len(downsampled))

        # Generate the matplotlib plot
        fig, ax = plt.subplots(figsize=(10, 3), dpi=100)
        ax.plot(time_axis, downsampled, color="gray", alpha=0.6)
        ax.set_yticks([])
        ax.set_xlim(0, duration_sec)

        # Plot selection vertical lines
        ax.axvline(x=start_val, color="green", linewidth=2, label="Start")
        ax.axvline(x=end_val, color="red", linewidth=2, label="End")
        ax.legend(loc="upper right")
        fig.tight_layout()
        
        # Render the plot directly into the web interface
        st.pyplot(fig)

        # 4. Playback and Export Segment
        st.subheader("🎧 Actions")
        start_ms = int(start_val * 1000)
        end_ms = int(end_val * 1000)
        trimmed_audio = audio[start_ms:end_ms]

        # Export to an in-memory buffer so it doesn't pollute the local disk
        from io import BytesIO
        buffer = BytesIO()
        trimmed_audio.export(buffer, format="mp3")
        buffer.seek(0)

        # HTML5 Web Audio Player for the selected region
        st.write("Preview selection:")
        st.audio(buffer, format="audio/mp3")

        # Native Web Download button
        st.download_button(
            label="💾 Download Trimmed Audio",
            data=buffer.getvalue(),
            file_name=f"trimmed_{uploaded_file.name.split('.')[0]}.mp3",
            mime="audio/mp3"
        )
