import Main from "../components/main/index"
import Best from "../components/best"
import Const from "../components/const"

export const routes = [
    { path: '*', component: <Main/> },
    { path: '', component: <Main/> },
    { path: 'best', component: <Best/> },
    { path: 'const', component: <Const/> },
]