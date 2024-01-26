import { Router } from './routers/router'
import { BrowserRouter } from 'react-router-dom'

const App = () => {
    return (
        <BrowserRouter>
            <Router/>
        </BrowserRouter>
    )
}

export default App