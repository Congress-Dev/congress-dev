import React, { createContext, useContext, useEffect } from "react";

import { PreferenceContext, PreferenceEnum } from "context";

export const ThemeContext = createContext();

const nivoBase = {
    text: {
        fontSize: 11,
        outlineWidth: 0,
    },
};

const nivoLight = Object.assign(
    {
        text: {
            fill: "#333333",
            outlineColor: "transparent",
        },
        axis: {
            domain: {
                line: {
                    stroke: "#777777",
                },
            },
            legend: {
                text: {
                    fill: "#333333",
                    outlineColor: "transparent",
                },
            },
            ticks: {
                line: {
                    stroke: "#777777",
                },
                text: {
                    fill: "#333333",
                    outlineColor: "transparent",
                },
            },
        },
        grid: {
            line: {
                stroke: "#dddddd",
            },
        },
        legends: {
            title: {
                text: {
                    fill: "#333333",
                    outlineColor: "transparent",
                },
            },
            text: {
                fill: "#333333",
                outlineColor: "transparent",
            },
            ticks: {
                line: {},
                text: {
                    fill: "#333333",
                    outlineColor: "transparent",
                },
            },
        },
        annotations: {
            text: {
                fill: "#333333",
                outlineColor: "#ffffff",
            },
            link: {
                stroke: "#000000",
                outlineColor: "#ffffff",
            },
            outline: {
                stroke: "#fff",
                outlineColor: "#eeeeee",
            },
            symbol: {
                fill: "#000000",
                outlineColor: "#ffffff",
            },
        },
        tooltip: {
            wrapper: {},
            container: {
                background: "#ffffff",
                color: "#333333",
            },
            basic: {},
            chip: {},
            table: {},
            tableCell: {},
            tableCellValue: {},
        },
    },
    nivoBase,
);

const nivoDark = Object.assign(
    {
        text: {
            fill: "#dddddd",
            outlineColor: "transparent",
        },
        labels: {
            text: {
                fill: "#dddddd"
            }
        },
        axis: {
            domain: {
                line: {
                    stroke: "#eee",
                },
            },
            legend: {
                title: {
                    text: {
                        fill: "#ddd"
                    }
                },
                text: {
                    fill: "#dddddd",
                    outlineColor: "transparent",
                },
                ticks: {
                    text: {
                        fill: "#ddd"
                    }
                }
            },
            ticks: {
                line: {
                    stroke: "#eee",
                },
                text: {
                    fill: "#dddddd",
                    outlineColor: "transparent",
                },
            },
        },
        grid: {
            line: {
                stroke: "#eee",
            },
        },
        legends: {
            title: {
                text: {
                    fill: "#dddddd",
                    outlineColor: "transparent",
                },
            },
            text: {
                fill: "#dddddd",
                outlineColor: "transparent",
            },
            ticks: {
                line: {},
                text: {
                    fill: "#dddddd",
                    outlineColor: "transparent",
                },
            },
        },
        annotations: {
            text: {
                fill: "#dddddd",
                outlineColor: "#000000",
            },
            link: {
                stroke: "#dddddd",
                outlineColor: "#000000",
            },
            outline: {
                stroke: "#252a31",
                outlineColor: "#1f2329",
            },
            symbol: {
                fill: "#dddddd",
                outlineColor: "#000000",
            },
        },
        tooltip: {
            wrapper: {},
            container: {
                background: "#000000",
                color: "#dddddd",
            },
            basic: {},
            chip: {},
            table: {},
            tableCell: {},
            tableCellValue: {},
        },
    },
    nivoBase,
);

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
                nivoTheme: preferences[PreferenceEnum.DARK_MODE]
                    ? nivoDark
                    : nivoLight,
            }}
        >
            {children}
        </ThemeContext.Provider>
    );
};
