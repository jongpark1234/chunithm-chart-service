import Decimal from 'decimal.js';

class Rank {
    static D: number = 0
    static C: number = 1
    static B: number = 2
    static BB: number = 3
    static BBB: number = 4
    static A: number = 5
    static AA: number = 6
    static AAA: number = 7
    static S: number = 8
    static Sp: number = 9
    static SS: number = 10
    static SSp: number = 11
    static SSS: number = 12
    static SSSp: number = 13
  
    static fromScore(score: number): number {
        if (score >= 1009000) return Rank.SSSp;
        if (score >= 1007500) return Rank.SSS;
        if (score >= 1005000) return Rank.SSp;
        if (score >= 1000000) return Rank.SS;
        if (score >= 990000) return Rank.Sp;
        if (score >= 975000) return Rank.S;
        if (score >= 950000) return Rank.AAA;
        if (score >= 925000) return Rank.AA;
        if (score >= 900000) return Rank.A;
        if (score >= 800000) return Rank.BBB;
        if (score >= 700000) return Rank.BB;
        if (score >= 600000) return Rank.B;
        if (score >= 500000) return Rank.C;
        return Rank.D;
    }

    static border(rank: number): Decimal {
        switch (rank) {
            case this.D: {
                return new Decimal(0);
            }
            case this.C: {
                return new Decimal(500000);
            }
            case this.B: {
                return new Decimal(600000);
            }
            case this.BB: {
                return new Decimal(700000);
            }
            case this.BBB: {
                return new Decimal(800000);
            }
            case this.A: {
                return new Decimal(900000);
            }
            case this.AA: {
                return new Decimal(925000);
            }
            case this.AAA: {
                return new Decimal(950000);
            }
            case this.S: {
                return new Decimal(975000);
            }
            case this.Sp: {
                return new Decimal(990000);
            }
            case this.SS: {
                return new Decimal(1000000);
            }
            case this.SSp: {
                return new Decimal(1005000);
            }
            case this.SSS: {
                return new Decimal(1007500);
            }
            case this.SSSp: {
                return new Decimal(1009000);
            }
        }
        return new Decimal(-1);
    }
}
  
export default Rank