import { useState, useRef, useEffect } from 'react';
import { useLocation } from '@tanstack/react-router';
import { chatWithAssistant } from '../api';

interface Message {
    id: number;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
}

const phaseGreetings: Record<string, { title: string; greeting: string }> = {
    'phase-1': {
        title: 'Script Selection',
        greeting: "Welcome to Phase 1! I can help you evaluate scripts, analyze genre trends, and assess concept viability. What would you like to explore?",
    },
    'phase-2': {
        title: 'Pre-Production',
        greeting: "Welcome to Phase 2! I'm here to assist with packaging strategy, budget planning, and talent acquisition decisions. How can I help?",
    },
    'phase-3': {
        title: 'Production',
        greeting: "Welcome to Phase 3! I can help track production health, manage shoot schedules, and flag risks. What do you need?",
    },
    'phase-4': {
        title: 'Post-Production',
        greeting: "Welcome to Phase 4! I can assist with edit analysis, market testing insights, and audience feedback strategies. Ask away!",
    },
    'phase-5': {
        title: 'Marketing',
        greeting: "Welcome to Phase 5! Let me help you plan campaigns, allocate marketing budgets, and identify target audiences. What's on your mind?",
    },
    'phase-6': {
        title: 'Distribution',
        greeting: "Welcome to Phase 6! I can guide you through distribution strategies, platform negotiations, and release timing. How can I assist?",
    },
    'phase-7': {
        title: 'Release',
        greeting: "Welcome to Phase 7! I'm here to help with release day monitoring, discoverability optimization, and audience engagement. What do you need?",
    },
    'phase-8': {
        title: 'Post-Release',
        greeting: "Welcome to Phase 8! I can help with revenue tracking, monetization strategies, and sequel potential analysis. Let's maximize returns!",
    },
};

const defaultGreeting = "Hi! I'm your FilmFlow assistant. Navigate to any project phase and I'll help you with phase-specific guidance and insights.";

function getPhaseFromPath(path: string): string | null {
    const match = path.match(/phase-(\d)/);
    return match ? `phase-${match[1]}` : null;
}

export default function ChatBot() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [currentPhase, setCurrentPhase] = useState<string | null>(null);
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const location = useLocation();

    // Update greeting when phase changes
    useEffect(() => {
        const phase = getPhaseFromPath(location.pathname);
        if (phase !== currentPhase) {
            setCurrentPhase(phase);
            if (phase && phaseGreetings[phase]) {
                setMessages((prev) => [
                    ...prev,
                    {
                        id: Date.now(),
                        text: phaseGreetings[phase].greeting,
                        sender: 'bot',
                        timestamp: new Date(),
                    },
                ]);
            }
        }
    }, [location.pathname, currentPhase]);

    // Initialize with default greeting
    useEffect(() => {
        if (messages.length === 0) {
            setMessages([
                {
                    id: Date.now(),
                    text: defaultGreeting,
                    sender: 'bot',
                    timestamp: new Date(),
                },
            ]);
        }
    }, [messages.length]);

    // Scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    // Focus input when chat opens
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 200);
        }
    }, [isOpen]);

    const handleSend = async () => {
        const text = inputValue.trim();
        if (!text || isTyping) return;

        const userMessage: Message = {
            id: Date.now(),
            text,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputValue('');
        setIsTyping(true);

        try {
            // Prepare history for context (last 5 messages)
            const history = messages.slice(-5).map(m => ({
                role: m.sender === 'user' ? 'user' : 'assistant',
                content: m.text
            }));

            const phase = getPhaseFromPath(location.pathname);
            const response = await chatWithAssistant({
                message: text,
                phase: phase,
                history: history
            });

            const botResponse: Message = {
                id: Date.now() + 1,
                text: response.text,
                sender: 'bot',
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, botResponse]);
        } catch (error) {
            const botError: Message = {
                id: Date.now() + 1,
                text: "I'm having trouble connecting to my brain right now. Please try again later.",
                sender: 'bot',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, botError]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const phaseKey = getPhaseFromPath(location.pathname);
    const activePhaseName = phaseKey ? phaseGreetings[phaseKey]?.title : null;

    return (
        <>
            {/* Chat Panel */}
            <div
                className={`fixed bottom-20 left-5 z-50 transition-all duration-300 ease-in-out ${isOpen
                    ? 'opacity-100 translate-y-0 pointer-events-auto'
                    : 'opacity-0 translate-y-4 pointer-events-none'
                    }`}
            >
                <div className="w-[380px] h-[520px] bg-card border border-border rounded-2xl shadow-2xl flex flex-col overflow-hidden">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-[#7c2d12] to-[#9a3412] px-5 py-4 flex items-center justify-between flex-shrink-0">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="text-white font-semibold text-sm">FilmFlow Assistant</h3>
                                {activePhaseName ? (
                                    <p className="text-white/70 text-xs">{activePhaseName} Phase</p>
                                ) : (
                                    <p className="text-white/70 text-xs">Ready to help</p>
                                )}
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="text-white/70 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10"
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M18 6 6 18" />
                                <path d="m6 6 12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Phase indicator pill */}
                    {activePhaseName && (
                        <div className="px-4 pt-3 pb-1 flex-shrink-0">
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-50 border border-orange-200 text-xs font-medium text-orange-800">
                                <span className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse" />
                                Active: {activePhaseName}
                            </span>
                        </div>
                    )}

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 scroll-smooth">
                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${msg.sender === 'user'
                                        ? 'bg-[#7c2d12] text-white rounded-br-md'
                                        : 'bg-muted text-foreground rounded-bl-md'
                                        }`}
                                >
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        {isTyping && (
                            <div className="flex justify-start">
                                <div className="bg-muted text-foreground rounded-2xl rounded-bl-md px-4 py-3 text-sm flex gap-1 items-center">
                                    <span className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '0s' }} />
                                    <span className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '0.2s' }} />
                                    <span className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '0.4s' }} />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="border-t border-border px-4 py-3 flex-shrink-0">
                        <div className="flex items-center gap-2">
                            <input
                                ref={inputRef}
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder={activePhaseName ? `Ask about ${activePhaseName}...` : 'Type a message...'}
                                className="flex-1 bg-muted rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[#7c2d12]/30 placeholder:text-muted-foreground/60 transition-shadow"
                            />
                            <button
                                onClick={handleSend}
                                disabled={!inputValue.trim()}
                                className="w-10 h-10 rounded-xl bg-[#7c2d12] text-white flex items-center justify-center hover:bg-[#9a3412] disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
                            >
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="m22 2-7 20-4-9-9-4z" />
                                    <path d="M22 2 11 13" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Floating Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`fixed bottom-5 left-5 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 ${isOpen
                    ? 'bg-[#7c2d12] rotate-0'
                    : 'bg-gradient-to-br from-[#7c2d12] to-[#9a3412] animate-[bounce-subtle_3s_ease-in-out_infinite]'
                    }`}
            >
                {isOpen ? (
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="m6 9 6 6 6-6" />
                    </svg>
                ) : (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                )}
                {/* Notification dot when not open */}
                {!isOpen && (
                    <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-white" />
                )}
            </button>
        </>
    );
}
