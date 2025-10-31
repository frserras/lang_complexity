import unit as U
import strategy as S

class Degrader:
    __strategies = {
        "deletion": S.Deletion,
        "replacement": S.Replacement,
        "sameness": S.Sameness,
        "random_char_replacementUnic": S.RandomCharReplacementUnic,
        "random_word_replacementUnic": S.RandomWordReplacementUnic,
        "word_shuffler": S.WordShuffle,
    }
    __units = {
        "chars": U.Chars(),
        "words": U.NotChar(r"\s"),
        "lines": U.NotChar("\n"),
    }

    def __init__(self, strategy: S.Strategy, unit: U.UnitParser):
        self.unit = unit
        self.strategy = strategy

    @classmethod
    def new(cls, strategy: str, unit: str, **strategy_arguments):
        unit = cls.__units[unit]
        strategy = cls.__strategies[strategy](**strategy_arguments)
        return cls(strategy, unit)

    def degrade(self, text: str) -> str:
        presult = self.unit.parse(text)
        #print(presult)
        output = self.strategy.execute(presult)
        return output