import axios from 'axios';
import * as fetchdata from '../../resources/fetchdata'
import { calcRating, parseWebElement } from "./index.module";
import chart from '../../resources/chart.json';


// const getPlayData = async () => {
//     try {
//         console.log('Accessing To CNBot Account...');
//         await axios.get(
//             fetchdata.LOGIN_URL,
//             { withCredentials: true }
//         ).then((res) => {
//             console.log(res)
//         })

//         const loginResponse = await session.post(
//             fetchdata.LOGIN_FETCH_URL,
//             fetchdata.LOGIN_PARAMS,
//             {
//                 params: fetchdata.LOGIN_PARAMS,
//                 headers: fetchdata.LOGIN_HEADERS,
//             }
//         );
    
//         const auth_token = (await session.get(loginResponse.headers.location)).headers['set-cookie'][0].split(';')[0].split('=')[1];
    
//         for (let diff = 0; diff < 5; diff++) {
//           console.log(`Fetching ${chart.difficulties[diff].name} Data...`);
    
//           const vsResult = await session.post(
//             CHUNITHM_VS_FETCH_URL,
//             {
//               genre: 99,
//               friend: 8038648670957,
//               radio_diff: diff,
//               loseOnly: 'on',
//               token: auth_token,
//             },
//             {
//               headers: VS_HEADERS,
//             }
//           );
    
//           const dom = new JSDOM(vsResult.data);
//           const namelist = Array.from(dom.window.document.querySelectorAll('.block_underline.text_b.text_c')).map((x) => x.textContent);
//           const scorelist = Array.from(dom.window.document.querySelectorAll('.play_musicdata_highscore')).map((x) => x.textContent).filter((_, index) => index % 2 !== 0);
    
//           parseWebElement(diff, namelist, scorelist);
//         }
//     } catch (error) {
//         console.error('Error:', error);
//     }
// }

const Best = () => {
    return <div>Best Chart Page</div>
}

export default Best