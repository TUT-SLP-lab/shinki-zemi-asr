import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


class ASRModel():
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model_id = "openai/whisper-large-v3"

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )

        self.processor = AutoProcessor.from_pretrained(self.model_id)

        self.pipe = pipeline("automatic-speech-recognition",
                             model=self.model,
                             tokenizer=self.processor.tokenizer,
                             feature_extractor=self.processor.feature_extractor,
                             torch_dtype=self.torch_dtype,
                             device=self.device,
                             return_timestamps=True,
                             generate_kwargs={"language": "ja"})

    def transcribe(self, audio_path : str):
        result = self.pipe(audio_path)
        return result


