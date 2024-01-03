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

    @property
    def min_score(self) -> int:
        match self.value:
            case 0:
                return 0
            case 1:
                return 500000
            case 2:
                return 600000
            case 3:
                return 700000
            case 4:
                return 800000
            case 5:
                return 900000
            case 6:
                return 925000
            case 7:
                return 950000
            case 8:
                return 975000
            case 9:
                return 990000
            case 10:
                return 1000000
            case 11:
                return 1005000
            case 12:
                return 1007500
            case 13:
                return 1009000