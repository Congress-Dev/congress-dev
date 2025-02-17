import React, { useContext, useEffect, useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { useLocation } from "react-router-dom";

import {
    Section,
    SectionCard,
    Card,
    Elevation,
    Button,
    InputGroup,
    NonIdealState,
    NonIdealStateIconSize,
} from "@blueprintjs/core";

import { talkToBill } from "common/api";
import { BillContext, LoginContext } from "context";

const TalkToBill = () => {
    const elementRef = useRef(null);
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

    useEffect(() => {
        if (elementRef.current) {
            elementRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

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
        <Section title="AI Insights" className="chat-popover-content">
            <SectionCard className="history">
                {messages.length == 0 && (
                    <NonIdealState
                        icon="predictive-analysis"
                        iconSize={NonIdealStateIconSize.STANDARD}
                        title="Chat with AI about this bill"
                        description={
                            <>
                                Ask questions about this bill
                                <br />
                                to gain more insight
                            </>
                        }
                        layout="vertical"
                    />
                )}
                {messages.map((msg, index) => (
                    <Card
                        key={index}
                        elevation={Elevation.TWO}
                        className={msg.sender}
                        ref={index === messages.length - 1 ? elementRef : null}
                    >
                        {msg.sender === "ai" &&
                            msg.tokens !== undefined &&
                            msg.time !== undefined && (
                                <div className="info">
                                    Tokens: {msg.tokens} | Time:{" "}
                                    {msg.time.toFixed(3)}s
                                </div>
                            )}
                        <div className="message">
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                    </Card>
                ))}
            </SectionCard>
            <SectionCard className="inputs">
                <InputGroup
                    fill={true}
                    placeholder="Enter your message..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => {
                        if (e.key === "Enter") sendMessage();
                    }}
                    rightElement={
                        <Button
                            icon="send-message"
                            intent="primary"
                            onClick={sendMessage}
                            style={{ marginLeft: "0.5rem" }}
                            disabled={!user}
                        />
                    }
                />
            </SectionCard>
        </Section>
    );
};

export default TalkToBill;
