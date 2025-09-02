import re

class Sequitur:
    _SEPARATOR = b'\xff\xfe\xff'
    _RULE_MARKER = b'@'

    @classmethod
    def _last_two_symbols(cls, input_bytes: bytes) -> tuple[bytes, bytes]:
        if len(input_bytes) < 2:
            return b'', input_bytes

        placeholder = -1
        if input_bytes[-1:] != cls._RULE_MARKER:
            last_symbol = input_bytes[-1:]
        else:
            placeholder = -2
            while input_bytes[placeholder:placeholder+1] != cls._RULE_MARKER:
                placeholder -= 1
            last_symbol = input_bytes[placeholder:]
        
        placeholder2 = placeholder - 1
        if input_bytes[placeholder2:placeholder2+1] != cls._RULE_MARKER:
            penultimate_symbol = input_bytes[placeholder2:placeholder]
        else:
            placeholder2 -= 1
            while input_bytes[placeholder2:placeholder2+1] != cls._RULE_MARKER:
                placeholder2 -= 1
            penultimate_symbol = input_bytes[placeholder2:placeholder]
            
        return penultimate_symbol, last_symbol

    @classmethod
    def _rule_utility(cls, rules: dict, unused_rules: list) -> tuple[bool, dict, list]:
        for rule in list(rules.keys()):
            if rule == b'0':
                continue

            count = 0
            other_keys = [k for k in rules if k != rule]
            for key in other_keys:
                count += len(re.findall(cls._RULE_MARKER + rule + cls._RULE_MARKER, rules[key]))
            
            if count < 2:
                rule_ref = cls._RULE_MARKER + rule + cls._RULE_MARKER
                rule_expansion = rules[rule]
                
                for key in other_keys:
                    rules[key] = rules[key].replace(rule_ref, rule_expansion)
                
                del rules[rule]
                unused_rules.append(rule)
                return False, rules, unused_rules
                
        return True, rules, unused_rules

    @classmethod
    def compress(cls, data: bytes) -> bytes:
        rules = {b'0': b''}
        num_rules = 0
        unused_rules = []

        for i in range(len(data)):
            rules[b'0'] += data[i:i+1]
            penult_symbol, last_symbol = cls._last_two_symbols(rules[b'0'])
            
            if not penult_symbol:
                continue
                
            last_digram = penult_symbol + last_symbol

            existing_rule_key = None
            for key, value in rules.items():
                if key != b'0' and value == last_digram:
                    existing_rule_key = key
                    break
            
            if existing_rule_key:
                rules[b'0'] = rules[b'0'][:-len(last_digram)] + cls._RULE_MARKER + existing_rule_key + cls._RULE_MARKER
            elif last_digram in rules[b'0'][:-len(last_digram)]:
                if unused_rules:
                    new_rule_key = unused_rules.pop(0)
                else:
                    num_rules += 1
                    new_rule_key = str(num_rules).encode('ascii')
                
                rules[new_rule_key] = last_digram
                rule_ref = cls._RULE_MARKER + new_rule_key + cls._RULE_MARKER
                rules[b'0'] = rules[b'0'].replace(last_digram, rule_ref)

            rule_utility_bool = False
            while not rule_utility_bool:
                rule_utility_bool, rules, unused_rules = cls._rule_utility(rules, unused_rules)

        main_string_bytes = rules.pop(b'0')
        rule_lines = []
        for key, value in rules.items():
            rule_lines.append(key + b'\t' + value)
        
        grammar_bytes = b'\n'.join(rule_lines)
        
        return main_string_bytes + cls._SEPARATOR + grammar_bytes

    @classmethod
    def decompress(cls, data: bytes) -> bytes:
        try:
            main_string, grammar_bytes = data.split(cls._SEPARATOR, 1)
        except ValueError:
            raise ValueError("Formato de dados comprimidos inválido: separador não encontrado.")

        rules = {}
        if grammar_bytes:
            for line in grammar_bytes.split(b'\n'):
                if line:
                    key, value = line.split(b'\t', 1)
                    rules[key] = value

        while cls._RULE_MARKER in main_string:
            found_replacement = False
            for key, value in rules.items():
                rule_ref = cls._RULE_MARKER + key + cls._RULE_MARKER
                if rule_ref in main_string:
                    main_string = main_string.replace(rule_ref, value)
                    found_replacement = True
            
            if not found_replacement:
                break
                
        return main_string

if __name__ == '__main__':
    texto_original = "ababcbabc".encode('utf-8')
    print(f"Texto Original: {texto_original.decode('utf-8')}")
    dados_comprimidos = Sequitur.compress(texto_original)
    print(f"Dados Comprimidos: {dados_comprimidos}")
    dados_descomprimidos = Sequitur.decompress(dados_comprimidos)
    print(f"Texto Descomprimido: {dados_descomprimidos.decode('utf-8')}")
    assert texto_original == dados_descomprimidos
    print("\nVerificação bem-sucedida: Original == Descomprimido")
    texto_original_2 = "O rato roeu a roupa do rei de roma. A rata roeu a roupa do rei de roma.".encode('utf-8')
    comprimido_2 = Sequitur.compress(texto_original_2)
    descomprimido_2 = Sequitur.decompress(comprimido_2)
    print(f"\nCompressão do texto 2 reduziu {len(texto_original_2)} bytes para {len(comprimido_2)} bytes.")
    assert texto_original_2 == descomprimido_2