import React, { useContext, useEffect, useState } from "react";
import { Card, Elevation, Button, InputGroup, H5 } from "@blueprintjs/core";
import { talkToBill } from "common/api";
import { useLocation } from "react-router-dom";
import { BillContext, LoginContext } from "context";
import ReactMarkdown from "react-markdown";

const TalkToBill = () => {
    const location = useLocation();
    const [messages, setMessages] = useState([]);
    const [query, setQuery] = useState("");
    const [versionId, setVersionId] = useState(undefined);
    const { bill } = useContext(BillContext);
    const { user } = useContext(LoginContext);

    useEffect(() => {
        bill?.legislation_versions?.forEach((version) => {
            if (
                version.legislation_version ==
                location.pathname.split("/").pop().split("?")[0]
            ) {
                setVersionId(version.legislation_version_id);
            }
        });
    }, [bill, location.pathname]);

    useEffect(() => {
        if (
            !user &&
            messages.slice(-1)[0]?.sender !== "gray" &&
            bill?.title &&
            bill?.title !== undefined
        ) {
            setMessages((prev) => [
                ...prev,
                {
                    sender: "gray",
                    content: `You must be logged in to chat with the ${bill.title}.`,
                    tokens: 0,
                    time: 0,
                },
            ]);
        }
    }, [user, bill]);
    
    const sendMessage = async () => {
        if (!query.trim()) return;
        if (!user) {
            setMessages((prev) => [
                ...prev,
                {
                    sender: "gray",
                    content: "You must be logged in to chat with Bill.",
                    tokens: 0,
                    time: 0,
                },
            ]);
        }
        // Append user's message
        const userMessage = { sender: "user", content: query };
        setMessages((prev) => [...prev, userMessage]);
        setQuery("");

        // Call the LLM API for a response
        try {
            const llmResponse = await talkToBill(versionId, query);
            const aiMessage = {
                sender: "ai",
                content: llmResponse.response,
                tokens: llmResponse.tokens,
                time: llmResponse.time,
            };
            setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
            console.error("Error calling LLM:", error);
            if (error.name?.startsWith("HTTP Error:")) {
                const errors = {
                    "HTTP Error: 429":
                        "I'm sorry, I can't respond to that right now. Please try again later. You are limited to 5 requests per 5 minutes",
                    "HTTP Error: 422":
                        "I'm sorry, I don't understand. Please try rephrasing your question.",
                    "HTTP Error: 413":
                        "I'm sorry, I can't respond to that right now. Your question is too long",
                };
                const aiMessage = {
                    sender: "warning",
                    content:
                        errors[error.name] ||
                        `I'm sorry, I can't respond to that right now. Please try again later. ${error.name}`,
                    tokens: 0,
                    time: 0,
                };
                setMessages((prev) => [...prev, aiMessage]);
            }
        }
    };

    return (
        <div
            style={{
                padding: "1rem",
                borderRight: "1px solid #ccc",
                height: "70vh",
                overflowY: "auto",
            }}
        >
            <H5>Chat</H5>
            <div style={{ marginBottom: "1rem" }}>
                {messages.map((msg, index) => (
                    <Card
                        key={index}
                        elevation={Elevation.TWO}
                        style={{
                            marginBottom: "0.5rem",
                            backgroundColor: {
                                ai: "#e8f5e9",
                                user: "#e3f2fd",
                                warning: "#ffeece",
                                gray: "#f5f5f5",
                            }[msg.sender],
                        }}
                    >
                        {msg.sender === "ai" &&
                            msg.tokens !== undefined &&
                            msg.time !== undefined && (
                                <div
                                    style={{
                                        fontSize: "0.6rem",
                                        marginBottom: "0.3rem",
                                        color: "#555",
                                    }}
                                >
                                    Tokens: {msg.tokens} | Time:{" "}
                                    {msg.time.toFixed(3)}s
                                </div>
                            )}
                        <div
                            style={{
                                fontSize: "0.7rem",
                                marginBottom: "0.3rem",
                                color: "#555",
                            }}
                        >
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                    </Card>
                ))}
            </div>
            <div style={{ display: "flex" }}>
                <InputGroup
                    placeholder="Enter your message..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => {
                        if (e.key === "Enter") sendMessage();
                    }}
                />
                <Button
                    icon="send"
                    intent="primary"
                    onClick={sendMessage}
                    style={{ marginLeft: "0.5rem" }}
                    disabled={!user}
                />
            </div>
        </div>
    );
};

export default TalkToBill;
