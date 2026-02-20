import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import gzip
import os
import warnings
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

class AlphaZipCompressor:
    def __init__(self, model_path="gpt2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading model on {self.device.upper()}...")

        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.max_length = self.model.config.max_position_embeddings
            
            print("Model and tokenizer loaded successfully.")
            print(f"Model maximum sequence length: {self.max_length} tokens.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            raise

    def compress_internal(self, test: str) -> bytes:
        all_ids = self.tokenizer.encode(test)
        initial_context_len = min(len(all_ids) // 4, self.max_length - 1)
        context_ids = all_ids[:initial_context_len]
        right_ids = all_ids[initial_context_len:]
        output_ranks = []

        with torch.no_grad():
            for i, right_token in enumerate(right_ids):
                input_tensor = torch.tensor([context_ids]).to(self.device)
                logits = self.model(input_ids=input_tensor).logits[:, -1, :]
                
                correct_token_logit = logits[0, right_token]
                rank = torch.sum(logits > correct_token_logit).item()
                output_ranks.append(str(rank))
                
                context_ids.append(right_token)
                context_ids = context_ids[-self.max_length:]

                if (i + 1) % 100 == 0:
                    print(f"Compressed {i + 1}/{len(right_ids)} tokens...")

        return ".".join(output_ranks).encode("utf-8")

alpha_object = AlphaZipCompressor()

def compress(dados_entrada: bytes) -> bytes:
    try:
        texto = dados_entrada.decode("utf-8")
    except UnicodeDecodeError:
        print("Warning: Input data is not valid UTF-8. Falling back to gzip.")
        return gzip.compress(dados_entrada)
        
    if len(texto) < 50:
        return gzip.compress(dados_entrada)
        
    return alpha_object.compress_internal(texto)

if __name__ == '__main__':
    with open("test_texto.txt", 'r', encoding='utf-8') as arquivo:
        texto = arquivo.read()
    dados_originais = texto.encode('utf-8')
    
    print(f"Iniciando compressão para texto de {len(dados_originais)} bytes...")
    dados_comprimidos = compress(dados_originais)
    
    print("\n--- Resultados ---")
    print(f"Tamanho original: {len(dados_originais)} bytes")
    print(f"Tamanho comprimido com AlphaZip: {len(dados_comprimidos)} bytes")
    print(f"Tamanho comprimido com Gzip: {len(gzip.compress(dados_originais))} bytes")
    
    taxa_alphazip = len(dados_originais) / len(dados_comprimidos)
    taxa_gzip = len(dados_originais) / len(gzip.compress(dados_originais))
    
    print(f"Taxa de compressão AlphaZip: {taxa_alphazip:.2f}x")
    print(f"Taxa de compressão Gzip: {taxa_gzip:.2f}x")