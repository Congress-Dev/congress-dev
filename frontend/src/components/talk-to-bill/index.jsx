import React, { useContext, useEffect, useState } from "react";
import { Card, Elevation, Button, InputGroup, H5 } from "@blueprintjs/core";
import { talkToBill } from "common/api";
import { useLocation } from "react-router-dom";
import { BillContext } from "context";
import ReactMarkdown from "react-markdown";

const TalkToBill = () => {
    const location = useLocation();
    console.log("Current URL:", location.pathname);
    const [messages, setMessages] = useState([]);
    const [query, setQuery] = useState("");
    const [versionId, setVersionId] = useState(undefined);
    const { bill } = useContext(BillContext);
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
    const sendMessage = async () => {
        if (!query.trim()) return;

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
            if (error.name === "HTTP Error: 429") {
                const aiMessage = {
                    sender: "warning",
                    content:
                        "I'm sorry, I can't respond to that right now. Please try again later. You are limited to 5 requests per 5 minutes",
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
                />
            </div>
        </div>
    );
};

export default TalkToBill;
