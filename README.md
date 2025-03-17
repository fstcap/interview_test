# interview_test  

## demo_video.mov is a demonstration file.

## Feature Description  
This is a meeting scheduling assistant. It determines whether to schedule a meeting through a conversation. If so, it extracts the meeting type, time range, and participants. If not, it informs the user of the tool's purpose. If the input information is incomplete, it prompts the user to provide the missing information.

## Project Environment  
- **Hardware:** MacBook Pro with Intel Integrated Graphics 8GB VRAM  
- **Software:** Python 3.9.6  
- 
## Set up LLM  
### Install Ollama and Configure the Environment
#### Download Ollama
Visit the official [Ollama website](https://ollama.com/download) and select the macOS version to directly download the installer package 256.  
Double-click the installer package to complete the installation. After installation, enter ollama --version in the terminal to verify if the installation was successful.
#### Download llama3.1-8B-Q4int  
```ollama pull llama3.1```  
#### Customize model parameters  
model parameters file is ./Modelfile
```ollama create my-custom-qwen -f Modelfile```  
#### Run Customize model  
```ollama run my-custom-qwen```
## Install project dependencies  
```pip install -r requirements.txt```

## Run the web server  
```python webapp.py```

## Access this address in the browser http://127.0.0.1:5001