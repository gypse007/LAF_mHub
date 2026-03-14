import { useState, useRef, useEffect } from 'react';
import { chatWithOpenclaw } from '../api';

interface Message {
    role: 'assistant' | 'user';
    content: string;
}

interface OpenClawChatProps {
    onComplete: (prompt: string) => void;
    wallTags: Record<string, string>;
}

export default function OpenClawChat({ onComplete, wallTags }: OpenClawChatProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: `Hi! I'm OpenClaw, your AI design concierge. Let's create your perfect mural. To get started, what is the **core subject** of the mural? (e.g., A cinematic video of a young Latina woman, or A hyperreal 3D render of a cyberpunk car...)`
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isManualMode, setIsManualMode] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isTyping) return;

        const userMsg = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsTyping(true);

        try {
            const historyPayload = messages.concat([{ role: 'user', content: userMsg }]);
            const data = await chatWithOpenclaw(historyPayload, wallTags);

            setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);

            if (data.finalPrompt) {
                setTimeout(() => {
                    onComplete(data.finalPrompt);
                }, 3000);
            }

        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I had a connection error. Could you repeat that?' }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className="openclaw-container" style={{ background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)', overflow: 'hidden', display: 'flex', flexDirection: 'column', height: '60vh', minHeight: '400px' }}>

            <div style={{ padding: '16px 20px', background: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ fontSize: '1.5rem' }}>🐾</div>
                    <div>
                        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>OpenClaw Concierge</h3>
                        <p style={{ margin: 0, fontSize: '0.8rem', opacity: 0.9 }}>8-Layer Cinematic Prompt Builder</p>
                    </div>
                </div>
                <button
                    onClick={() => setIsManualMode(!isManualMode)}
                    className="btn"
                    style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: 'none', padding: '6px 12px', fontSize: '0.85rem' }}
                >
                    {isManualMode ? 'Switch to AI Chat' : 'Skip & Type Manually'}
                </button>
            </div>

            {isManualMode ? (
                <div style={{ flex: 1, padding: 24, display: 'flex', flexDirection: 'column', gap: 16, background: 'var(--background)' }}>
                    <h4 style={{ margin: 0 }}>Manual Prompt Entry</h4>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        Skip the AI concierge and write your own SDXL prompt directly.
                    </p>
                    <textarea
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        placeholder="A cinematic 8k render of a cyberpunk city at night with neon lights..."
                        style={{ flex: 1, padding: 16, borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text)', outline: 'none', resize: 'none', fontFamily: 'inherit' }}
                    />
                    <button
                        onClick={() => onComplete(input)}
                        disabled={!input.trim()}
                        className="btn btn-primary"
                        style={{ padding: '12px' }}
                    >
                        🚀 Generate Mural
                    </button>
                </div>
            ) : (
                <>
                    <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
                        {messages.map((msg, i) => (
                            <div key={i} style={{
                                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                background: msg.role === 'user' ? 'var(--primary)' : 'var(--background)',
                                color: msg.role === 'user' ? 'white' : 'var(--text)',
                                padding: '12px 16px',
                                borderRadius: '16px',
                                borderBottomRightRadius: msg.role === 'user' ? 4 : 16,
                                borderBottomLeftRadius: msg.role === 'assistant' ? 4 : 16,
                                maxWidth: '85%',
                                border: msg.role === 'assistant' ? '1px solid var(--border)' : 'none',
                                lineHeight: 1.5,
                                fontSize: '0.95rem'
                            }}>
                                <span dangerouslySetInnerHTML={{ __html: msg.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
                            </div>
                        ))}
                        {isTyping && (
                            <div style={{ alignSelf: 'flex-start', background: 'var(--background)', padding: '12px 16px', borderRadius: '16px', borderBottomLeftRadius: 4, border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                                <span className="typing-dots">OpenClaw is typing...</span>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <form onSubmit={handleSubmit} style={{ padding: 16, borderTop: '1px solid var(--border)', display: 'flex', gap: 12, background: 'var(--background)' }}>
                        <input
                            type="text"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            placeholder="Describe your vision..."
                            disabled={isTyping}
                            style={{ flex: 1, padding: '12px 16px', borderRadius: 24, border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text)', outline: 'none' }}
                        />
                        <button type="submit" disabled={!input.trim() || isTyping} className="btn btn-primary" style={{ borderRadius: 24, padding: '0 24px' }}>
                            Send
                        </button>
                    </form>
                </>
            )}

        </div>
    );
}
