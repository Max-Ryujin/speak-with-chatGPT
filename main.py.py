import whisper
from gtts import gTTS
import pyaudio
import wave
import keyboard
import os
import playsound
from chatgpt_wrapper import ChatGPT
import time


chunk = 1024 

# 16 bits per sample
sample_format = pyaudio.paInt16 
chanels = 1
 
# Record at 44400 samples per second
smpl_rt = 44400 


def speak(s):
    myoutput = gTTS(text=s, lang='en', slow=False)
    myoutput.save("~\\output.mp3")
    playsound.playsound('~\\output.mp3')
    os.remove('~\\output.mp3')    
pass

if __name__ == "__main__":

    # Initialize the ChatGPT Model for Transcribing Messages
    bot = ChatGPT()

    # Create an interface to PortAudio
    pa = pyaudio.PyAudio() 

    #load whisper model
    model = whisper.load_model("base")

    while True:
        frames = [] 
        if(keyboard.read_key() == "r"):

            #recording 
            print('Recording...')
            stream = pa.open(format=sample_format, channels=chanels,
                    rate=smpl_rt, input=True,
                    frames_per_buffer=chunk)
            while(keyboard.is_pressed("r")):
                data = stream.read(chunk)
                frames.append(data)
            stream.stop_stream()
            stream.close()

            #transcripe to wav file

            print('processing...')      
            sf = wave.open("~\\x.wav", 'wb')
            sf.setnchannels(chanels)
            sf.setsampwidth(pa.get_sample_size(sample_format))
            sf.setframerate(smpl_rt)
            sf.writeframes(b''.join(frames))
            sf.close()
            
            #transcripe with Whisper
            print("Transcribe...")
            result = model.transcribe("~\\x.wav")
            print(result["text"])

            #call chatGPT api function
            response = bot.ask(result["text"])

            speak(response)


       

