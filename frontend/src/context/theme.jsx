import React, { createContext, useContext } from "react";

import { PreferenceContext, PreferenceEnum } from "context";

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
    const { preferences, setPreference } = useContext(PreferenceContext);

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
