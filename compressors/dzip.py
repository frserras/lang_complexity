import subprocess
import tempfile
import os
import platform
import gzip

PATH_PARA_REPOSITORIO_DZIP = './compressors/Dzip-torch'
PATH_PARA_MODELO_BOOTSTRAP = os.path.join(PATH_PARA_REPOSITORIO_DZIP, 'Models', 'text8_bstrap')

class DZipCompressor:
    def __init__(self, dzip_repo_path: str, bootstrap_model_path: str):
        if platform.system() == "Windows":
            raise NotImplementedError("DZip utiliza scripts de shell e pode não ser compatível com Windows.")
        self.dzip_repo_path = os.path.abspath(dzip_repo_path)
        self.compress_script_path = os.path.join(self.dzip_repo_path, 'coding-gpu', 'compress.sh')
        self.bootstrap_model_path = os.path.abspath(bootstrap_model_path)
        if not os.path.isfile(self.compress_script_path):
            raise FileNotFoundError(f"Script de compressão não encontrado em: {self.compress_script_path}")
        if not os.path.isfile(self.bootstrap_model_path):
            raise FileNotFoundError(f"Modelo bootstrap não encontrado em: {self.bootstrap_model_path}")

    def compress(self, input_bytes: bytes) -> bytes:
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as temp_in:
            temp_in.write(input_bytes)
            input_filepath = temp_in.name
            
        output_filepath = input_filepath + ".dzip"
        actual_output_filepath = output_filepath + ".combined"

        try:
            command = ['bash', self.compress_script_path, input_filepath, output_filepath, 'com', self.bootstrap_model_path]
            working_directory = os.path.dirname(self.compress_script_path)
            
            subprocess.run(command, check=True, cwd=working_directory, capture_output=True, text=True)

            with open(actual_output_filepath, 'rb') as f_out:
                compressed_bytes = f_out.read()
            return compressed_bytes
            
        except subprocess.CalledProcessError as e:
            print("Erro ao executar o script de compressão do DZip.")
            print(f"stderr:\n{e.stderr}")
            raise
        finally:
            if os.path.exists(input_filepath):
                os.remove(input_filepath)
            if os.path.exists(output_filepath):
                os.remove(output_filepath)
            if os.path.exists(actual_output_filepath):
                os.remove(actual_output_filepath)

try:
    dzip_object = DZipCompressor(
        dzip_repo_path=PATH_PARA_REPOSITORIO_DZIP,
        bootstrap_model_path=PATH_PARA_MODELO_BOOTSTRAP
    )
except FileNotFoundError as e:
    dzip_object = None
    print(f"Não foi possível inicializar o DZip.")
    print(f"Detalhe do erro: {e}")

def compress(dados_entrada: bytes) -> bytes:
    if dzip_object is None:
        raise RuntimeError("O compressor DZip não foi inicializado corretamente devido a um erro de configuração.")
    
    try:
        texto = dados_entrada.decode('utf-8')
        if len(texto) < 10000:
            print("Aviso: Dados de entrada muito curtos. Usando gzip como fallback para maior eficiência.")
            return gzip.compress(dados_entrada)
    except UnicodeDecodeError:
        print("Aviso: Os dados de entrada não são UTF-8 válidos. Usando gzip como fallback.")
        return gzip.compress(dados_entrada)
    
    return dzip_object.compress(dados_entrada)

if __name__ == '__main__':
    if dzip_object:
        with open("test_texto.txt", 'r', encoding='utf-8') as arquivo:
            texto = arquivo.read()
        dados_originais = texto.encode('utf-8')
        
        print(f"Tamanho original: {len(dados_originais)} bytes")
        dados_comprimidos = compress(dados_originais)
        print(f"Tamanho comprimido: {len(dados_comprimidos)} bytes")