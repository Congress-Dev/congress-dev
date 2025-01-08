import React, { createContext, useState } from "react";
import { GoogleOAuthProvider, useGoogleLogin } from "@react-oauth/google";
import jwtDecode from "jwt-decode";

export const LoginContext = createContext();

export const LoginProvider = ({ children }) => {
    const [user, setUser] = useState(null); // State to store user info

    const handleLoginSuccess = (credentialResponse) => {
        const decoded = jwtDecode(credentialResponse.credential); // Decode the JWT
        setUser({
            name: decoded.name,
            email: decoded.email,
            picture: decoded.picture, // User's profile picture
        });
        console.log("User Info:", decoded); // Log the user info for debugging
    }

    function handleLoginFailure() {
        console.error("Login Failed");
    }

    const handleLogin = useGoogleLogin({
        onSuccess: (credentialResponse) => {
            console.log(credentialResponse)
            const decoded = jwtDecode(credentialResponse.credential); // Decode the JWT
            setUser({
                name: decoded.name,
                email: decoded.email,
                picture: decoded.picture, // User's profile picture
            });
            console.log("User Info:", decoded);
        },
        onError: handleLoginFailure,
    });

    function handleLogout() {
        setUser(null); // Clear user info on logout
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
