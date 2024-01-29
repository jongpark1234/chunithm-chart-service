import axios from 'axios';
import * as fetchdata from '../../resources/fetchdata'
import { calcRating, parseWebElement } from "./index.module";
import chart from '../../resources/chart.json';
import { useEffect, useState } from 'react';

const Best = () => {
    const [getMessage, setMessage] = useState<String>('');
    useEffect(() => {
        axios.get(fetchdata.LOGIN_URL, {
            withCredentials: true
        }).then((data) => {
            setMessage(data.data)
        }).catch((error) => {
            console.log(error)
        })
    }, [])
    return <div>{getMessage}</div>
}

export default Best