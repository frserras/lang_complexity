# sequitur_paralelo.py
import sys
import time
from mpi4py import MPI

class Sequitur:
    # Separador para serializar a gramática em bytes
    _SEPARATOR = b'\xff\xfe\xff'

    @classmethod
    def _rule_utility(cls, rules: dict, unused_rules: list) -> tuple[bool, dict, list]:
        """Verifica e remove regras usadas menos de duas vezes."""
        for rule in list(rules.keys()):
            if rule == b'0':
                continue
            
            count = 0
            other_keys = [k for k in rules if k != rule]
            for key in other_keys:
                count += rules[key].count(b'@' + rule + b'@')

            if count < 2:
                rule_ref = b'@' + rule + b'@'
                rule_expansion = rules[rule]
                for key in other_keys:
                    rules[key] = rules[key].replace(rule_ref, rule_expansion)
                del rules[rule]
                unused_rules.append(rule)
                return False, rules, unused_rules
        return True, rules, unused_rules

    @classmethod
    def _last_two_symbols(cls, input_bytes: bytes) -> tuple[bytes, bytes]:
        """Extrai os dois últimos símbolos (bytes ou regras) da sequência."""
        if len(input_bytes) < 2:
            return b'', input_bytes

        placeholder = -1
        if input_bytes[-1:] != b'@':
            last_symbol = input_bytes[-1:]
        else:
            placeholder = -2
            while input_bytes[placeholder:placeholder+1] != b'@':
                placeholder -= 1
            last_symbol = input_bytes[placeholder:]
        
        placeholder2 = placeholder - 1
        if input_bytes[placeholder2:placeholder2+1] != b'@':
            penultimate_symbol = input_bytes[placeholder2:placeholder]
        else:
            placeholder2 -= 1
            while input_bytes[placeholder2:placeholder2+1] != b'@':
                placeholder2 -= 1
            penultimate_symbol = input_bytes[placeholder2:placeholder]
        return penultimate_symbol, last_symbol

    @classmethod
    def _run_serial_sequitur(cls, input_chunk: bytes) -> dict:
        """Executa o algoritmo Sequitur serial em um pedaço de dados."""
        num_rules = 0
        unused_rules = []
        rules = {b'0': b''}

        for i in range(len(input_chunk)):
            rules[b'0'] += input_chunk[i:i+1]
            penult_symbol, last_symbol = cls._last_two_symbols(rules[b'0'])
            
            if not penult_symbol:
                continue
            
            last_digram = penult_symbol + last_symbol
            
            string_occurrences = last_digram in rules[b'0'][:-len(last_digram)]
            
            # Lógica principal de criação e substituição de regras
            # (Simplificada para brevidade, mas segue a lógica original)
            if string_occurrences:
                if not unused_rules:
                    num_rules += 1
                    new_rule_key = str(num_rules).encode('ascii')
                else:
                    new_rule_key = unused_rules.pop(0)
                
                rules[new_rule_key] = last_digram
                rule_ref = b'@' + new_rule_key + b'@'
                rules[b'0'] = rules[b'0'].replace(last_digram, rule_ref)
                
                # Verificação de utilidade da regra
                utility_ok = False
                while not utility_ok:
                    utility_ok, rules, unused_rules = cls._rule_utility(rules, unused_rules)
        return rules

    @classmethod
    def _merge_and_replace(cls, list_of_grammars: list) -> tuple[dict, int]:
        """Funde múltiplas gramáticas parciais em uma só."""
        master_rules = {}
        back_dict = {}
        num_rules = 0

        # Renumera todas as regras para evitar colisões
        for grammar in list_of_grammars:
            for key, value in grammar.items():
                if key == b'0':
                    continue
                if value not in back_dict:
                    num_rules += 1
                    new_key = str(num_rules).encode('ascii')
                    back_dict[value] = new_key
                    master_rules[new_key] = value
                    
                # Substitui a chave antiga pela nova no texto principal
                old_ref = b'@' + key + b'@'
                new_ref = b'@' + back_dict[value] + b'@'
                grammar[b'0'] = grammar[b'0'].replace(old_ref, new_ref)

        # Concatena os textos principais
        master_string = b''.join([g[b'0'] for g in list_of_grammars])
        master_rules[b'0'] = master_string
        
        return master_rules, num_rules

    @classmethod
    def _finalize_grammar(cls, rules: dict) -> dict:
        """Aplica passes de otimização na gramática fundida."""
        # A lógica de `digram_uniqueness` e múltiplos passes de `rule_utility`
        # seriam aplicados aqui na gramática `rules`.
        # Por simplicidade, faremos apenas um passe de `rule_utility`.
        utility_ok = False
        unused_rules = []
        while not utility_ok:
            utility_ok, rules, unused_rules = cls._rule_utility(rules, unused_rules)
        return rules

    @classmethod
    def compress(cls, data: bytes) -> bytes or None:
        """
        Orquestra a compressão paralela usando MPI.
        Retorna os bytes comprimidos no rank 0, e None nos outros.
        """
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        data_chunk = None
        if rank == 0:
            if not data:
                # Envia um sinal para outros processos terminarem se não houver dados
                for i in range(1, size):
                    comm.send(None, dest=i)
                return b''

            # Divide os dados para os processos
            chunk_size = len(data) // size
            for i in range(1, size):
                start = i * chunk_size
                end = (i + 1) * chunk_size if i != size - 1 else len(data)
                comm.send(data[start:end], dest=i)
            data_chunk = data[0:chunk_size]
        else:
            data_chunk = comm.recv(source=0)

        if data_chunk is None:
            return None

        # Cada processo roda o Sequitur em seu pedaço
        local_grammar = cls._run_serial_sequitur(data_chunk)
        
        # Coleta os resultados no rank 0
        all_grammars = comm.gather(local_grammar, root=0)

        if rank == 0:
            # Fusão e finalização
            merged_grammar, _ = cls._merge_and_replace(all_grammars)
            final_grammar = cls._finalize_grammar(merged_grammar)
            
            # Serialização para bytes
            main_string = final_grammar.pop(b'0')
            rule_lines = []
            for key, value in final_grammar.items():
                rule_lines.append(key + b'\t' + value)
            grammar_bytes = b'\n'.join(rule_lines)
            
            return main_string + cls._SEPARATOR + grammar_bytes
        
        return None

    @classmethod
    def decompress(cls, compressed_data: bytes) -> bytes:
        """Descomprime um fluxo de bytes (método serial)."""
        try:
            main_string, grammar_bytes = compressed_data.split(cls._SEPARATOR, 1)
        except (ValueError, IndexError):
            return compressed_data # Retorna original se o formato for inválido

        rules = {}
        if grammar_bytes:
            for line in grammar_bytes.split(b'\n'):
                if line:
                    parts = line.split(b'\t', 1)
                    if len(parts) == 2:
                        rules[parts[0]] = parts[1]

        # Expansão iterativa das regras
        # Um número fixo de passes para evitar loops infinitos com gramáticas malformadas
        for _ in range(len(rules) + 1): 
            for key, value in rules.items():
                rule_ref = b'@' + key + b'@'
                main_string = main_string.replace(rule_ref, value)
        
        return main_string


# Ponto de entrada para execução com MPI
if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    input_data = None
    if rank == 0:
        if len(sys.argv) != 2:
            print("Uso: mpiexec -n <num_procs> python sequitur_paralelo.py <arquivo>")
            # Encerra outros processos
            for i in range(1, size):
                comm.send(None, dest=i)
            sys.exit(1)
        
        input_file = sys.argv[1]
        try:
            with open(input_file, 'rb') as f:
                input_data = f.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo '{input_file}' não encontrado.")
            for i in range(1, size):
                comm.send(None, dest=i)
            sys.exit(1)

    # Inicia a compressão em todos os processos
    start_time = time.time()
    compressed_result = Sequitur.compress(input_data)
    end_time = time.time()

    if rank == 0:
        print(f"Compressão paralela com {size} processos concluída.")
        print(f"Tamanho Original: {len(input_data)} bytes")
        print(f"Tamanho Comprimido: {len(compressed_result)} bytes")
        print(f"Tempo: {end_time - start_time:.4f} s")
        
        # Demonstração da descompressão
        decompressed_data = Sequitur.decompress(compressed_result)
        if decompressed_data == input_data:
            print("Verificação bem-sucedida: Dados descomprimidos correspondem ao original.")
        else:
            print("Erro na verificação: Dados descomprimidos NÃO correspondem ao original.")