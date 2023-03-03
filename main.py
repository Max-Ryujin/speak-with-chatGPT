from gtts import gTTS
import pyaudio
import wave
import sys
import keyboard
import os
import openai
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup


chunk = 1024 

# 16 bits per sample
sample_format = pyaudio.paInt16 
chanels = 1
 
# Record at 44400 samples per second
smpl_rt = 44400 

openai.api_key = os.getenv("OPENAI_API_KEY")

#check if language is supported and set language variable to the correct language code
# check if args[1] is empty because if it is empty the language variable will be set to english
if(len(sys.argv) == 1 or sys.argv[1] == "en" or sys.argv[1] == "english" or sys.argv[1] == "englisch"):
    language = "en"
elif(sys.argv[1] == "de" or sys.argv[1] == "german" or sys.argv[1] == "deutsch"):
    language = "de"
else:
    print("Language not supported")
    exit()

#function to speak the output 
def speak(s):
    myoutput = gTTS(text=s, lang=language, slow=False)
    myoutput.save("output.mp3")
    tts = AudioSegment.from_mp3('output.mp3')
    output = speedup(tts,1.5,150)
    output.export("file.mp3", format="mp3")
    play(output)
    os.remove('output.mp3')    

pass

if __name__ == "__main__":

    message_history = [{"role": "system", "content": "You are Jarvis, a virtual assistant. You give short answers to questions and never say more then 3 sentences."}]

    # Create an interface to PortAudio
    pa = pyaudio.PyAudio() 
    speak("Hello, I am Jarvis. How can I help you?")
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

            #transcripe to wav file and save it
            print('processing...')      
            sf = wave.open("x.wav", 'wb')
            sf.setnchannels(chanels)
            sf.setsampwidth(pa.get_sample_size(sample_format))
            sf.setframerate(smpl_rt)
            sf.writeframes(b''.join(frames))
            sf.close()
            
            #transcribe the audio file
            print("Transcribe...")
            file = open("x.wav", "rb")
            transcription = openai.Audio.transcribe("whisper-1", file)
            message_history.append({"role": "user", "content": transcription['text']})
            print(transcription)

            #call chatGPT api function
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=message_history)
            
            #save the completion as a message
            message_history.append({"role": "system", "content": completion['choices'][0]['message']['content']})

            #print the output and speak it
            print("\n ------------------ \n")
            print(completion['choices'][0]['message']['content'])
            speak(completion['choices'][0]['message']['content'])
