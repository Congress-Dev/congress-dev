import React, { createContext, useState } from "react";

export const PreferenceDefaults = Object.freeze({
    DARK_MODE: false,
    HIGHLIGHT_DATES: false,
    HIGHLIGHT_DOLLARS: false,
    HIGHLIGHT_ACTIONS: false,
});

export const PreferenceEnum = Object.freeze({
    DARK_MODE: "DARK_MODE",
    HIGHLIGHT_DATES: "HIGHLIGHT_DATES",
    HIGHLIGHT_DOLLARS: "HIGHLIGHT_DOLLARS",
    HIGHLIGHT_ACTIONS: "HIGHLIGHT_ACTIONS",
});

export const PreferenceContext = createContext();

export const PreferenceProvider = ({ children }) => {
    const storagePreferences = {};

    Object.keys(PreferenceEnum).forEach((key) => {
        const value = localStorage.getItem(key);
        storagePreferences[key] =
            value != null ? JSON.parse(value) : PreferenceDefaults[key];
    });

    const [_preferences, _setPreferences] = useState(storagePreferences);

    function setPreference(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
        _setPreferences({
            ..._preferences,
            [key]: value,
        });
    }

    return (
        <PreferenceContext.Provider
            value={{ preferences: _preferences, setPreference }}
        >
            {children}
        </PreferenceContext.Provider>
    );
};
