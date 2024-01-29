import { Route, Routes } from 'react-router-dom'
import { routes } from './routes'
import * as style from './router.style'

import Navbar from '../components/common/navbar/index'
import Footer from '../components/common/footer/index'

export const Router = () => {
    return <>
        <Navbar />
        <style.background>
            <Routes>
                {
                    routes.map((element, idx) => {
                        return (
                            <Route path={element.path} element={element.component} key={idx}/>
                            )
                        })
                    }
            </Routes>
        </style.background>
        <Footer/>
    </>
}