import styled from "styled-components";

export const background = styled.div`
    width: 100%;
    height: 60px;
    display: flex;
    background-color: black;
`

export const navElement = styled.div`
    min-width: 100px;
    width: 10%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    background-color: rgb(0, 0, 0);
    font-weight: bold;
    transition: .15s ease-in-out;
    cursor: pointer;
    &:hover {
        background-color: rgb(50, 50, 50);
    }
`