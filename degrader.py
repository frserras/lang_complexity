import warnings
import unit as U
import strategy as S


class Degrader:
    __strategies = {
        "deletion": S.Deletion,
        "replacement": S.Replacement,
        "sameness": S.Sameness,
    }
    __units = {
        "chars": U.Chars(),
        "words": U.NotChar("\s"),
        "lines": U.NotChar("\n"),
    }

    def __init__(self, strategy: S.Strategy, unit: U.UnitParser):

        if (
            isinstance(strategy, S.Replacement)
            and (
                isinstance(unit, U.Chars)
                or (isinstance(unit, U.NotChar) and unit.char == "\n")
            )
        ):
                warnings.warn(
                "This combination of strategy and unit is not covered"
                "by tests, as it is not used in any of "
                "the metrics implemented in the library.",
                UserWarning,
                stacklevel=2
            )

        self.unit = unit
        self.strategy = strategy

    @classmethod
    def new(cls, strategy: str, unit: str, **strategy_arguments):
        unit = cls.__units[unit]
        strategy = cls.__strategies[strategy](**strategy_arguments)
        return cls(strategy, unit)

    def degrade(self, text: str) -> str:
        presult = self.unit.parse(text)
        output = self.strategy.execute(presult)
        return output
