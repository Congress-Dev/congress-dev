import React, { createContext, useContext, useEffect } from "react";

import { PreferenceContext, PreferenceEnum } from "context";

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
    const { preferences, setPreference } = useContext(PreferenceContext);

    useEffect(() => {
        if (preferences[PreferenceEnum.DARK_MODE]) {
            window.root.classList.add("bp5-dark");
        } else {
            window.root.classList.remove("bp5-dark");
        }
    }, [preferences[PreferenceEnum.DARK_MODE]]);

    function setDarkMode(value) {
        setPreference(PreferenceEnum.DARK_MODE, value);
    }

    return (
        <ThemeContext.Provider
            value={{
                isDarkMode: preferences[PreferenceEnum.DARK_MODE],
                setDarkMode,
            }}
        >
            {children}
        </ThemeContext.Provider>
    );
};
