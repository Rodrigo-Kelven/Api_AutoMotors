import React from "react";
import "./header.css"

const Header = () => {
    return(

        <header className="header">

            <div className="logo"><a href="#">AutoMotors</a></div>

        
            <nav>
                <ul>
                    <li><a href="#">Contato</a></li>
                    <div className="divisao"></div>
                    <li><a href="#">Sobre</a></li>
                </ul>
            </nav>

        </header>



    )
}

export default Header;