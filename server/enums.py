from enum import Enum

class Rank(Enum):
    D = 0
    C = 1
    B = 2
    BB = 3
    BBB = 4
    A = 5
    AA = 6
    AAA = 7
    S = 8
    Sp = 9
    SS = 10
    SSp = 11
    SSS = 12
    SSSp = 13

    def __str__(self) -> str:
        return self.name.replace('p', '+')

    @classmethod
    def from_score(cls, score: int):
        if score >= 1009000:
            return cls.SSSp
        if score >= 1007500:
            return cls.SSS
        if score >= 1005000:
            return cls.SSp
        if score >= 1000000:
            return cls.SS
        if score >= 990000:
            return cls.Sp
        if score >= 975000:
            return cls.S
        if score >= 950000:
            return cls.AAA
        if score >= 925000:
            return cls.AA
        if score >= 900000:
            return cls.A
        if score >= 800000:
            return cls.BBB
        if score >= 700000:
            return cls.BB
        if score >= 600000:
            return cls.B
        if score >= 500000:
            return cls.C
        return cls.D

    @classmethod
    def border(cls, rank: int) -> int:
        match rank:
            case cls.D:
                return 0
            case cls.C:
                return 500000
            case cls.B:
                return 600000
            case cls.BB:
                return 700000
            case cls.BBB:
                return 800000
            case cls.A:
                return 900000
            case cls.AA:
                return 925000
            case cls.AAA:
                return 950000
            case cls.S:
                return 975000
            case cls.Sp:
                return 990000
            case cls.SS:
                return 1000000
            case cls.SSp:
                return 1005000
            case cls.SSS:
                return 1007500
            case cls.SSSp:
                return 1009000