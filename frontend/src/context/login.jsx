import React, { createContext, useState, useEffect } from "react";
import { useGoogleLogin } from "@react-oauth/google";

import { userLogin, userLogout, userGet } from "common/api";

export const LoginContext = createContext();

export const LoginProvider = ({ children }) => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        userGet().then((response) => {
            setUser(response);
        });
    }, []);

    const handleLoginSuccess = (authObject) => {
        userLogin(authObject.access_token, authObject.expires_in).then(
            (response) => {
                setUser(response);
            },
        );
    };

    function handleLoginFailure() {
        console.error("Login Failed");
    }

    const handleLogin = useGoogleLogin({
        onSuccess: handleLoginSuccess,
        onError: handleLoginFailure,
    });

    function handleLogout() {
        userLogout().then(() => {
            setUser(null);
        });
    }

    return (
        <LoginContext.Provider
            value={{
                user,
                handleLogin,
                handleLogout,
            }}
        >
            {children}
        </LoginContext.Provider>
    );
};
