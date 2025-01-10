import React, { createContext, useState, useEffect, useMemo } from "react";
import { useGoogleLogin } from "@react-oauth/google";

import {
    userLogin,
    userLogout,
    userGet,
    userGetLegislation,
    userGetLegislator,
} from "common/api";

export const LoginContext = createContext();

export const LoginProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [favoriteBills, setFavoriteBills] = useState(null);
    const [favoriteSponsors, setFavoriteSponsors] = useState(null);

    const favoriteBillIds = useMemo(() => {
        if (favoriteBills == null) {
            return [];
        }

        return favoriteBills.map((item) => item.legislation_id);
    }, [favoriteBills]);

    const favoriteSponsorIds = useMemo(() => {
        if (favoriteSponsors == null) {
            return [];
        }

        return favoriteSponsors.map((item) => item.id);
    }, [favoriteSponsors]);

    useEffect(() => {
        userGet().then((response) => {
            setUser(response);
        });
    }, []);

    useEffect(() => {
        if (user == null) {
            return;
        }

        userGetLegislation().then((response) => {
            if (response?.legislation != null) {
                setFavoriteBills(response.legislation);
            }
        });

        userGetLegislator().then((response) => {
            if (response?.legislation != null) {
                setFavoriteSponsors(response.legislation);
            }
        });
    }, [user]);

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
                favoriteBills,
                favoriteBillIds,
                setFavoriteBills,
                favoriteSponsors,
                favoriteSponsorIds,
                setFavoriteSponsors,
            }}
        >
            {children}
        </LoginContext.Provider>
    );
};
