"""
Speech-to-Text processing module using Vosk
"""
import os
import json
import asyncio
import wave
from typing import Dict, List
from pydub import AudioSegment
import ffmpeg
from vosk import Model, KaldiRecognizer
from .tasks import update_task_status
from .config import MODELS_DIR, INPUT_DIR, OUTPUT_DIR
from .utils import cleanup_temp_files, generate_vtt_subtitle

async def process_audio_file(file, language: str, model_size: str, task_id: str):
    """
    Process audio file using Vosk - wrapper for background processing
    """
    # Save uploaded file first
    input_file_path = os.path.join(INPUT_DIR, f"{task_id}_{file.filename}")
    
    # Write file content
    with open(input_file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # For now, return immediately - actual processing will be in background
    return {"status": "queued", "task_id": task_id}

def process_audio_sync(input_file_path: str, language: str, model_size: str, task_id: str):
    """
    Synchronous audio processing for background tasks
    """
    temp_files = []
    
    try:
        # Update task status to processing
        update_task_status(task_id, "processing")
        
        # Convert to WAV if needed
        audio_file_path = convert_to_wav_sync(input_file_path)
        temp_files.append(audio_file_path)
        
        # Get model path
        model_path = os.path.join(MODELS_DIR, language, model_size)
        
        # Process with Vosk
        result = transcribe_with_vosk_sync(audio_file_path, model_path)
        
        # Save results
        output_text_path = os.path.join(OUTPUT_DIR, f"{task_id}.txt")
        output_json_path = os.path.join(OUTPUT_DIR, f"{task_id}.json")
        
        # Save text result
        with open(output_text_path, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        # Save full result with segments
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Update task status with result
        update_task_status(task_id, "done", result=result)
        
        return result
        
    except Exception as e:
        # Update task status with error
        update_task_status(task_id, "failed", error=str(e))
        raise e
    finally:
        # Clean up temporary files
        cleanup_temp_files(temp_files)

def convert_to_wav_sync(input_file_path: str) -> str:
    """
    Convert audio to WAV format (synchronous)
    """
    output_file_path = input_file_path.replace(os.path.splitext(input_file_path)[1], ".wav")
    
    try:
        # Use pydub to convert
        audio = AudioSegment.from_file(input_file_path)
        # Convert to mono and set sample rate to 16kHz for Vosk
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_file_path, format="wav")
        
        return output_file_path
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")

def transcribe_with_vosk_sync(audio_file_path: str, model_path: str) -> Dict:
    """
    Transcribe audio file using Vosk model (synchronous)
    """
    # Check if model exists
    if not os.path.exists(model_path):
        raise Exception(f"Model not found at {model_path}. Please ensure models are downloaded.")
    
    try:
        # Load model
        model = Model(model_path)
        
        # Open WAV file
        wf = wave.open(audio_file_path, 'rb')
        
        # Verify audio format
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise Exception("Audio file must be WAV format mono PCM 16kHz")
        
        # Create recognizer
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)  # Enable word-level timestamps
        
        # Process audio
        segments = []
        full_text = ""
        total_confidence = 0
        word_count = 0
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get('text'):
                    segments.append(result)
                    full_text += result['text'] + " "
                    
                    # Calculate confidence from words
                    for word in result.get('result', []):
                        if 'conf' in word:
                            total_confidence += word['conf']
                            word_count += 1
        
        # Get final result
        final_result = json.loads(rec.FinalResult())
        if final_result.get('text'):
            segments.append(final_result)
            full_text += final_result['text']
            
            # Add final confidence
            for word in final_result.get('result', []):
                if 'conf' in word:
                    total_confidence += word['conf']
                    word_count += 1
        
        wf.close()
        
        # Calculate average confidence
        avg_confidence = total_confidence / word_count if word_count > 0 else 0.0
        
        # Process segments for VTT
        vtt_segments = []
        for segment in segments:
            if segment.get('result'):
                for i, word in enumerate(segment['result']):
                    start_time = word.get('start', 0)
                    end_time = word.get('end', start_time + 1)
                    text = word.get('word', '')
                    
                    vtt_segments.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text
                    })
        
        # Group words into sentences for better VTT display
        sentence_segments = group_words_into_sentences(vtt_segments)
        
        return {
            'text': full_text.strip(),
            'confidence': round(avg_confidence, 3),
            'segments': segments,
            'vtt_segments': sentence_segments
        }
        
    except Exception as e:
        raise Exception(f"Speech recognition failed: {str(e)}")

def group_words_into_sentences(word_segments: List[Dict], max_duration: float = 5.0) -> List[Dict]:
    """
    Group words into sentences for better subtitle display
    """
    if not word_segments:
        return []
    
    sentences = []
    current_sentence = {
        'start': word_segments[0]['start'],
        'end': word_segments[0]['end'],
        'text': word_segments[0]['text']
    }
    
    for word in word_segments[1:]:
        # Check if we should start a new sentence
        duration = word['end'] - current_sentence['start']
        gap = word['start'] - current_sentence['end']
        
        if duration > max_duration or gap > 1.0:  # 1 second gap or max duration
            sentences.append(current_sentence)
            current_sentence = {
                'start': word['start'],
                'end': word['end'],
                'text': word['text']
            }
        else:
            # Add to current sentence
            current_sentence['end'] = word['end']
            current_sentence['text'] += ' ' + word['text']
    
    # Add the last sentence
    if current_sentence['text']:
        sentences.append(current_sentence)
    
    return sentences

# Legacy async functions for compatibility
async def convert_to_wav(input_file_path: str) -> str:
    """Convert to WAV (async wrapper)"""
    return convert_to_wav_sync(input_file_path)

async def transcribe_with_vosk(audio_file_path: str, model_path: str) -> str:
    """Transcribe with Vosk (async wrapper) - returns only text for compatibility"""
    result = transcribe_with_vosk_sync(audio_file_path, model_path)
    return result['text']