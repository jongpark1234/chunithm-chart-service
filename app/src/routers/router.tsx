import { Route, Routes } from 'react-router-dom'
import { routes } from './routes'
import * as style from './router.style'

export const Router = () => {
    return (
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
    )
}