import Decimal from "decimal.js";

import Rank from "../../classes/rank";
import chart from '../../resources/chart.json';

export const parseWebElement = (diff: number, namelist: string[], scorelist: string[]): void => {
    const result = [];
    for (const song of chart.songs) {
        if (song.category === "WORLD'S END") {
            continue;
        }
    
        if (namelist.includes(song.title)) {
            const curidx: number = namelist.indexOf(song.title);
        
            const name: string = namelist[curidx]; // 이름 ( str )
            const score: string = scorelist[curidx]; // 점수 ( str )
            const scoreValue: Decimal = new Decimal(score.replace(/,/g, '')); // 점수 ( Decimal )
            const diffValue: string = ['basic', 'advanced', 'expert', 'master', 'ultima'][diff]; // 난이도 ( str )
            const level: string = song.sheets[diff].internalLevel; // 레벨 ( str )
            const levelValue: Decimal = new Decimal(song.sheets[diff].internalLevelValue); // 레벨 ( Decimal )
            const ratingValue: Decimal = calcRating(scoreValue, levelValue); // 레이팅 ( Decimal )
            const rating: string = ratingValue.mul(100).floor().div(100).toString(); // 레이팅 ( str )
            const image: string = 'https://dp4p6x0xfi5o9.cloudfront.net/chunithm/img/cover/' + song.imageName; // 커버 이미지 ( str )
        
            // ret 배열에 저장
            result.push({ name, score, scoreValue, diff, diffValue, level, levelValue, rating, ratingValue, image });
        }
    }
}

export const calcRating = (score: Decimal, internal_level: Decimal): Decimal => {
    const baselvl: Decimal = internal_level.mul(10_000);
    let rating: Decimal;

    if (score >= Rank.border(Rank.SSSp)) {
        rating = Decimal.add(baselvl, 21_500);

    } else if (score >= Rank.border(Rank.SSS)) {
        rating = baselvl.plus(
            Decimal.sub(score, Rank.border(Rank.SSS)).plus(20_000)
        );

    } else if (score >= Rank.border(Rank.SSp)) {
        rating = baselvl.plus(
            Decimal.sub(score, Rank.border(Rank.SSp)).mul(2).plus(15_000)
        );

    } else if (score >= Rank.border(Rank.SS)) {
        rating = baselvl.plus(
            Decimal.sub(score, Rank.border(Rank.SS)).plus(10_000)
        );

    } else if (score >= Rank.border(Rank.S)) {
        rating = baselvl.plus(
            Decimal.sub(score, Rank.border(Rank.S)).mul(2).div(5)
        );

    } else if (score >= Rank.border(Rank.A)) {
        rating = baselvl.minus(
            Decimal.sub(score, Rank.border(Rank.A)).mul(2).div(3).plus(50_000)
        );

    } else if (score >= Rank.border(Rank.BBB)) {
        rating = Decimal.add(
            Decimal.sub(baselvl, 50_000).div(2),
            Decimal.mul(
                Decimal.sub(score, Rank.border(Rank.BBB)),
                Decimal.sub(baselvl, 50_000).div(2)
            ).div(100_000)
        );

    } else if (score >= Rank.border(Rank.C)) {
        rating = Decimal.mul(
            Decimal.sub(baselvl, 50_000).div(2),
            Decimal.sub(score, Rank.border(Rank.C))
        ).div(300_000);

    } else {
        rating = new Decimal(0);

    }

    return Decimal.div(rating, 10_000);
}