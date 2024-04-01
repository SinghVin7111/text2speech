import os
import streamlit as st  # Streamlit library for creating web apps
from pydub import AudioSegment  # Audio processing library
import requests  # Library for making HTTP requests
from dotenv import load_dotenv  # Library for loading environment variables


# At the beginning of your script, load the environment variables
load_dotenv()

class TextToSpeechApp:
    def __init__(self):
        self.temp_file = "temp.mp3"
        self.processed_file = "processed.wav"

    def synthesize_text(self, text: str) -> bool:
        # Load the API key from an environment variable
        api_key = os.getenv('XI_API_KEY')

        # API endpoint for text-to-speech service
        url = "https://api.elevenlabs.io/v1/text-to-speech/NWUmRK8Ke0m8Ms5lYVru/stream"
        # Headers for the HTTP request including the API key loaded from the environment variable
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key  # Use the loaded API key here
        }
# Data payload for the request including the text to be synthesized
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2"
            # Add other settings like voice settings if needed
        }

        # Make a POST request to the API with the specified headers and data
        response = requests.post(url, json=data, headers=headers, stream=True)

        # Check if the response is successful (HTTP status code 200)
        if response.status_code == 200:
            # Write the content of the response to a temporary file
            with open(self.temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            return True
        else:
            # If the request failed, display an error message on the Streamlit app
            st.error(f"Failed to synthesize text: {response.text}")
            return False

    # Method to process the audio file by adjusting its speed
    def process_audio_file(self, speed: float) -> str:
        try:
            # Load the temporary audio file
            audio = AudioSegment.from_file(self.temp_file)
            # Adjust the speed of the audio
            audio = self.adjust_audio_speed(audio, speed)
        
            # Create a filename for the processed audio file
            processed_filename = os.path.splitext(self.temp_file)[0] + '_processed.wav'
            # Export the processed audio with specific parameters
            audio.export(processed_filename, format='wav', parameters=["-ac", "1", "-ar", "11025", "-acodec", "pcm_u8", "-sample_fmt", "u8"])
            return processed_filename
        except Exception as e:
            # If an error occurs during processing, display an error message on the Streamlit app
            st.error(f"Error occurred during audio processing: {e}")
            return ""

    # Static method to adjust the speed of an audio segment
    @staticmethod
    def adjust_audio_speed(audio: AudioSegment, speed: float) -> AudioSegment:
        if speed == 1.0:  # No change in speed
            return audio
        elif speed > 1.0:  # Speed up the audio
            # Speed up by increasing the number of frames per second
            return audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * speed)
            }).set_frame_rate(audio.frame_rate)
        else:  # Slow down the audio
            # Slow down by reducing the number of frames per second
            slowed_down = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * speed)
            })
            return slowed_down.set_frame_rate(audio.frame_rate)

    # Main method to run the Streamlit app
    def run(self):
        # Set the title of the Streamlit app
        st.title("ITS Text-to-Speech App")

        # Create a text area for users to enter text to synthesize
        announcement_text = st.text_area("Enter text to synthesize", height=150)
        # Create a slider for users to adjust the speed of speech
        speed = st.slider("Adjust Speed of Speech", 0.5, 2.0, 1.0, 0.1)

        # Create a button to process the entered text
        if st.button("Process"):
            if announcement_text:
                # Synthesize the entered text and process the audio file
                if self.synthesize_text(announcement_text):
                    processed_filename = self.process_audio_file(speed)
                    if processed_filename:
                        # Play the processed audio file in the Streamlit app
                        st.audio(processed_filename, format='audio/wav')
                    # Clean up the original temporary file
                    os.remove(self.temp_file)
                    # Update the processed file name for cleanup purposes
                    self.processed_file = processed_filename
                else:
                    # Display an error message if text synthesis fails
                    st.error("Could not synthesize the text, please check the input or try again later.")
            else:
                # Display a warning message if no text is entered
                st.warning("Please enter the text you'd like to synthesize.")

        # Create a button to clear the processed audio file
        if st.button("Clear"):
            if os.path.exists(self.processed_file):
                # Clean up the processed file
                os.remove(self.processed_file)

# Entry point for the script
if __name__ == "__main__":
    # Instantiate the TextToSpeechApp class
    app = TextToSpeechApp()
    # Run the Streamlit app
    app.run()
