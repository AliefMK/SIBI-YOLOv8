from google.cloud import texttospeech
import os

def main():
    # Example text to convert to speech
    text = "Halo, ini adalah contoh teks yang akan diubah menjadi suara."
    
    # Output filename for the audio file
    output_filename = "output.mp3"
    
    # Call the text-to-speech function
    text_to_speech(text, output_filename)

def text_to_speech(text, output_filename):
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "SIBIKEY.json"
    
    # Create a Text-to-Speech client
    client = texttospeech.TextToSpeechClient()
    
    # Prepare the text input for synthesis
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    # Set the voice parameters
    voice = texttospeech.VoiceSelectionParams(
        language_code="id-ID",  # Use "id-ID" for Indonesian
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    
    # Set the audio configuration
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    # Perform the text-to-speech synthesis
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    # Write the response to an output file
    with open(output_filename, "wb") as out:
        out.write(response.audio_content)
        print(f"Audio content written to file: {output_filename}")
    
if __name__ == "__main__":
    main()