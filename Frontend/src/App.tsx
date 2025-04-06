import React, { useState, useEffect } from 'react';
import { Bot, Send, User, Sparkles, Heart, Shield, MessageSquare, Moon, Sun, StickyNote, X, Plus, Pencil, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Utility function to summarize tips
function summarizeTip(line: string): string {
  return line.trim();
}

// Extract tips from bot response
function extractTips(text: string): string[] {
  const lines = text.split('\n');
  const tipsSet = new Set<string>();

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      let bullet = trimmed.replace(/^[-*]\s+/, '');
      bullet = summarizeTip(bullet);
      tipsSet.add(bullet);
    }
  }
  return Array.from(tipsSet);
}

// Define message interface with id and optional isTyping flag
interface Message {
  id: string;
  text: string;
  isUser: boolean;
  isTyping?: boolean;
}

// Define note interface
interface Note {
  id: string;
  content: string;
  timestamp: string;
}

function App() {
  // Initial chat messages with unique IDs
  const [messages, setMessages] = useState<Message[]>([
    {
      id: crypto.randomUUID(),
      text: "Hi, I'm Alora! I'm here to help you manage stress. How are you feeling today?",
      isUser: false,
    },
  ]);

  const [input, setInput] = useState('');
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark');
    }
    return false;
  });

  const [isNotesOpen, setIsNotesOpen] = useState(false);
  const [notes, setNotes] = useState<Note[]>([]);
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [stressValue, setStressValue] = useState<number | null>(null); // Changed to null for initial "-"

  // Apply dark mode class to document
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  // Add a new note
  const addNote = (content: string) => {
    const newNote: Note = {
      id: crypto.randomUUID(),
      content,
      timestamp: new Date().toLocaleString(),
    };
    setNotes((prev) => [newNote, ...prev]);
  };

  // Delete a note
  const deleteNote = (id: string) => {
    setNotes((prev) => prev.filter((note) => note.id !== id));
  };

  // Start editing a note
  const startEditing = (note: Note) => {
    setEditingNoteId(note.id);
    setEditContent(note.content);
  };

  // Save an edited note
  const saveEdit = (id: string) => {
    if (editContent.trim()) {
      setNotes((prev) =>
        prev.map((note) =>
          note.id === id
            ? { ...note, content: editContent.trim(), timestamp: new Date().toLocaleString() + ' (edited)' }
            : note
        )
      );
    }
    setEditingNoteId(null);
    setEditContent('');
  };

  // Cancel note edit
  const cancelEdit = () => {
    setEditingNoteId(null);
    setEditContent('');
  };

  // Stress condition logic
  const getStressCondition = (val: number) => {
    if (val < 1) return "No stress";
    if (val < 2) return "Mild stress";
    if (val < 3) return "Moderate stress";
    if (val < 4) return "High stress";
    return "Extreme stress";
  };

  // Map stress value to color
  const getStressColor = (val: number) => {
    const hue = 120 - val * 24;
    return `hsl(${hue}, 100%, 50%)`;
  };

  // Handle message submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessageId = crypto.randomUUID();
    const typingMessageId = crypto.randomUUID();

    setMessages((prev) => [
      ...prev,
      { id: userMessageId, text: input, isUser: true },
      { id: typingMessageId, text: 'Alora is typing...', isUser: false, isTyping: true },
    ]);
    setInput('');

    try {
      const response = await fetch('http://localhost:8001/process_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      let bot_response = data.bot_response.trim();
      if (
        (bot_response.startsWith('"') && bot_response.endsWith('"')) ||
        (bot_response.startsWith("'") && bot_response.endsWith("'"))
      ) {
        bot_response = bot_response.slice(1, -1);
      }
      const stress_level = data.stress_level;
      console.log('Received stress_level:', stress_level); // Log for debugging

      // Handle stress_level robustly
      if (stress_level != null) {
        const parsedStress = typeof stress_level === 'number' ? stress_level : parseFloat(stress_level);
        if (!isNaN(parsedStress)) {
          setStressValue(parsedStress);
        } else {
          console.error('Invalid stress_level value:', stress_level);
        }
      } else {
        console.error('stress_level not found in response');
      }

      setMessages((prev) => {
        const index = prev.findIndex((msg) => msg.id === typingMessageId);
        if (index !== -1) {
          const newMessages = [...prev];
          newMessages[index] = { id: typingMessageId, text: bot_response, isUser: false };
          return newMessages;
        }
        return [...prev, { id: crypto.randomUUID(), text: bot_response, isUser: false }];
      });

      const tips = extractTips(bot_response);
      tips.forEach((tip) => addNote(tip));
    } catch (error: any) {
      setMessages((prev) => {
        const index = prev.findIndex((msg) => msg.id === typingMessageId);
        if (index !== -1) {
          const newMessages = [...prev];
          newMessages[index] = { id: typingMessageId, text: 'Error: ' + error.message, isUser: false };
          return newMessages;
        }
        return [...prev, { id: crypto.randomUUID(), text: 'Error: ' + error.message, isUser: false }];
      });
    }
  };

  // Donut gauge styles (moved inside render to handle null case)
  const donutStyle: React.CSSProperties = stressValue != null
    ? {
        background: `conic-gradient(${getStressColor(stressValue)} 0% ${(stressValue / 5) * 100}%, #444 ${(stressValue / 5) * 100}% 100%)`,
        borderRadius: '50%',
        width: '60px',
        height: '60px',
        position: 'relative',
      }
    : {
        background: '#444',
        borderRadius: '50%',
        width: '60px',
        height: '60px',
        position: 'relative',
      };

  const donutHoleStyle: React.CSSProperties = {
    background: isDark ? '#1f2937' : '#ffffff',
    borderRadius: '50%',
    width: '44px',
    height: '44px',
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    fontSize: '1.2rem',
    color: isDark ? '#fff' : '#000',
  };

  return (
    <div
      className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-200"
      style={{
        backgroundSize: '400% 400%',
        animation: 'gradient 15s ease infinite',
      }}
    >
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-sm transition-colors duration-200">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
              <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Alora</h1>
            </div>
            <div className="flex items-center gap-6">
              <button
                onClick={() => setIsDark(!isDark)}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                aria-label="Toggle theme"
              >
                {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
              <nav className="hidden md:flex items-center gap-6">
                <a
                  href="#features"
                  className="text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                >
                  Features
                </a>
                <a
                  href="#about"
                  className="text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                >
                  About
                </a>
                <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                  Get Started
                </button>
              </nav>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-6 pl-24">
        <div className="max-w-5xl mx-auto">
          {/* Hero Section */}
          <section className="text-center mb-10">
            <h2 className="text-4xl font-bold text-gray-800 dark:text-white mb-4">Alora</h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-6">
              Your Personal Stress Management Assistant
            </p>
          </section>

          {/* Chat Interface */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl shadow-xl overflow-hidden transition-colors duration-200">
            <div className="h-[500px] flex flex-col">
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex items-start gap-2 max-w-[80%] ${
                        message.isUser ? 'flex-row-reverse' : ''
                      }`}
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
                          message.isUser
                            ? 'bg-indigo-100 dark:bg-indigo-900'
                            : 'bg-purple-100 dark:bg-purple-900'
                        }`}
                      >
                        {message.isUser ? (
                          <User className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                        ) : (
                          <Bot className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                        )}
                      </div>
                      <div
                        className={`rounded-2xl px-4 py-2 ${
                          message.isUser
                            ? 'bg-indigo-600 text-white'
                            : message.isTyping
                            ? 'bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400 italic'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                        }`}
                      >
                        {message.isTyping ? (
                          'Alora is typing...'
                        ) : (
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              p: ({ node, children, ...props }) => (
                                <p className="mb-4" {...props}>
                                  {children}
                                </p>
                              ),
                              ul: ({ node, children, ...props }) => (
                                <ul className="list-disc ml-6 mb-4" {...props}>
                                  {children}
                                </ul>
                              ),
                              li: ({ node, children, ...props }) => (
                                <li className="mb-2" {...props}>
                                  {children}
                                </li>
                              ),
                            }}
                          >
                            {message.text}
                          </ReactMarkdown>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <form
                onSubmit={handleSubmit}
                className="p-4 border-t border-gray-200 dark:border-gray-700"
              >
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2 focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-400 transition-colors"
                  />
                  <button
                    type="submit"
                    className="bg-indigo-600 text-white rounded-lg px-4 py-2 hover:bg-indigo-700 transition-colors"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Features Section */}
          <section id="features" className="py-16">
            <h3 className="text-2xl font-bold text-center text-gray-800 dark:text-white mb-8">
              Why Choose Alora?
            </h3>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 shadow-sm hover:shadow-md transition-all">
                <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900 rounded-lg flex items-center justify-center mb-4">
                  <Sparkles className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                </div>
                <h4 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">
                  AI-Powered Support
                </h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Advanced algorithms to understand and respond to your emotional needs.
                </p>
              </div>
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 shadow-sm hover:shadow-md transition-all">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-4">
                  <Heart className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <h4 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">
                  Compassionate Care
                </h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Empathetic responses designed to provide comfort and understanding.
                </p>
              </div>
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 shadow-sm hover:shadow-md transition-all">
                <div className="w-12 h-12 bg-pink-100 dark:bg-pink-900 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-pink-600 dark:text-pink-400" />
                </div>
                <h4 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">
                  Private & Secure
                </h4>
                <p className="text-gray-600 dark:text-gray-300">
                  Your conversations are always private and protected.
                </p>
              </div>
            </div>
          </section>

          {/* About Section */}
          <section id="about" className="py-16">
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl p-8 shadow-xl transition-colors duration-200">
              <div className="flex items-center gap-4 mb-6">
                <MessageSquare className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
                <h3 className="text-2xl font-bold text-gray-800 dark:text-white">About Alora</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                Alora is an advanced AI chatbot designed to help you manage stress and anxiety through
                supportive conversations. Using cutting-edge natural language processing, Alora provides
                personalized support while helping you develop healthy coping mechanisms for stress management.
              </p>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-50/80 dark:bg-gray-900/80 backdrop-blur-sm border-t border-gray-200 dark:border-gray-800 transition-colors duration-200">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-gray-600 dark:text-gray-400">
            <p>© 2025 Alora. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Floating Notes Button */}
      <button
        onClick={() => setIsNotesOpen(!isNotesOpen)}
        className="fixed bottom-6 right-6 w-12 h-12 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg flex items-center justify-center transition-colors duration-200 z-50"
        aria-label="Toggle notes"
      >
        <StickyNote className="w-6 h-6" />
      </button>

      {/* Floating Notes Panel */}
      {isNotesOpen && (
        <div className="fixed bottom-24 right-6 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl overflow-hidden z-50">
          <div className="p-4 bg-indigo-600 text-white flex items-center justify-between">
            <h4 className="font-semibold">Important Notes</h4>
            <button
              onClick={() => setIsNotesOpen(false)}
              className="text-white/80 hover:text-white transition-colors"
              aria-label="Close notes"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notes.map((note) => (
              <div key={note.id} className="p-4 border-b border-gray-200 dark:border-gray-700">
                {editingNoteId === note.id ? (
                  <div className="space-y-2">
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      className="w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200"
                      rows={3}
                      autoFocus
                    />
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => saveEdit(note.id)}
                        className="p-1 text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
                        aria-label="Save edit"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="p-1 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                        aria-label="Cancel edit"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="text-gray-800 dark:text-gray-200 text-sm">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{note.content}</ReactMarkdown>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{note.timestamp}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => startEditing(note)}
                        className="text-gray-400 hover:text-indigo-500 transition-colors"
                        aria-label="Edit note"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteNote(note.id)}
                        className="text-gray-400 hover:text-red-500 transition-colors"
                        aria-label="Delete note"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => addNote('Stay hydrated and take breaks regularly!')}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-400 rounded-lg hover:bg-indigo-200 dark:hover:bg-indigo-800 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Note</span>
            </button>
          </div>
        </div>
      )}

      {/* Floating Stress Donut */}
      <div
        className="fixed bottom-6 left-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 flex items-center gap-3 text-gray-800 dark:text-gray-200"
        style={{ width: '160px', zIndex: 60 }}
      >
        <div style={{ position: 'relative' }}>
          <div style={donutStyle}>
            <div style={donutHoleStyle}>
              {stressValue != null ? stressValue.toFixed(1) : '-'}
            </div>
          </div>
        </div>
        <div className="text-sm font-semibold">
          {stressValue != null ? getStressCondition(stressValue) : 'Awaiting input'}
        </div>
      </div>
    </div>
  );
}

export default App;