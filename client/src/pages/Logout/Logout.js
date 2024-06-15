import React, { useEffect } from "react";
import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import AuthContext from "../../context/AuthContext";

const Logout = () => {
    const navigate = useNavigate();
    const { logout } = useContext(AuthContext);

    useEffect(() => {
        logout(`${window.REACT_APP_BACKEND_HOST}/logout`);
        navigate("/login");
    }, []);
}

export default Logout;