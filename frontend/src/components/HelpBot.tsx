'use client';

import { FormEvent, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bot, MessageSquare, Send, X, Loader2 } from 'lucide-react';
import GlassFrame from './GlassFrame';

const quickPrompts = [
  'How do I sign in?',
  'What does SecureShift monitor?',
  'How do I add a repository?',
];

const answers: Record<string, string> = {
  'How do I sign in?':
    'Click "Sign In" on the home page, enter your email and password. New users can create an account by clicking "Sign Up" instead.',
  'What does SecureShift monitor?':
    'SecureShift scans your GitHub repositories for security vulnerabilities using multiple tools (Bandit, Safety, TruffleHog) and provides AI-powered fix suggestions.',
  'How do I add a repository?':
    'In the dashboard, enter your GitHub repository URL in the "Add Repository" section and click "Add Repository". The system will automatically scan it for vulnerabilities.',
};

const fallbackResponse =
  'SecureShift AI can help with sign-in, repository scanning, vulnerability monitoring, and navigating the security dashboard.';

interface HelpBotProps {
  open: boolean;
  onClose: () => void;
}

export default function HelpBot({ open, onClose }: HelpBotProps) {
  const [selectedPrompt, setSelectedPrompt] = useState(quickPrompts[0]);
  const [customQuestion, setCustomQuestion] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const response = useMemo(() => {
    if (aiResponse) return aiResponse;
    return answers[selectedPrompt] ?? fallbackResponse;
  }, [selectedPrompt, aiResponse]);

  const handlePromptSelect = (prompt: string) => {
    setSelectedPrompt(prompt);
    setCustomQuestion('');
    setAiResponse('');
  };

  const handleAsk = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const question = customQuestion.trim();
    if (!question) {
      return;
    }

    setIsLoading(true);
    setSelectedPrompt(question);
    setAiResponse('');

    try {
      const response = await fetch('http://localhost:8000/api/chatbot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: question }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('API Error:', errorData);
        throw new Error(errorData.detail || 'Failed to get AI response');
      }

      const data = await response.json();
      setAiResponse(data.response);
      setCustomQuestion('');
    } catch (error) {
      console.error('Error getting AI response:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      if (errorMessage.includes('rate-limited') || errorMessage.includes('429')) {
        setAiResponse('The AI service is temporarily busy. Please try again in a moment or select a quick prompt above.');
      } else if (errorMessage.includes('timeout')) {
        setAiResponse('The AI is taking too long to respond. Please try again or select a quick prompt above.');
      } else {
        setAiResponse('Sorry, I encountered an error. Please try again or select a quick prompt above.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {open ? (
        <motion.div
          initial={{ opacity: 0, y: -10, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -12, scale: 0.98 }}
          transition={{ duration: 0.2 }}
          className="absolute right-0 top-[calc(100%+14px)] z-50 w-[360px] max-w-[calc(100vw-2rem)]"
        >
          <GlassFrame className="rounded-3xl p-4 shadow-[0_24px_80px_-32px_rgba(255,255,255,0.3)]">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/[0.08] text-primary">
                  <Bot className="h-5 w-5" />
                </span>
                <div>
                  <p className="text-sm font-semibold text-on-background">SecureShift AI Bot</p>
                  <p className="text-xs uppercase tracking-[0.2em] text-on-surface-variant">
                    Instant Help
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="rounded-full border border-white/10 bg-white/[0.04] p-2 text-on-surface-variant transition-colors hover:text-on-surface"
                aria-label="Close AI bot"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-4 rounded-2xl border border-white/8 bg-black/30 p-4">
              <div className="flex items-start gap-3">
                <span className="mt-1 text-primary">
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <MessageSquare className="h-4 w-4" />
                  )}
                </span>
                <div>
                  <p className="text-sm font-medium text-on-background">{selectedPrompt}</p>
                  <p className="mt-2 text-sm leading-6 text-on-surface-variant">
                    {isLoading ? 'Thinking...' : response}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => handlePromptSelect(prompt)}
                  className={`w-full rounded-2xl border px-4 py-3 text-left text-sm transition-all ${
                    selectedPrompt === prompt
                      ? 'border-white/20 bg-white/[0.08] text-on-background'
                      : 'border-white/8 bg-white/[0.03] text-on-surface-variant hover:bg-white/[0.06] hover:text-on-surface'
                  }`}
                >
                  {prompt}
                </button>
              ))}
            </div>

            <form
              onSubmit={handleAsk}
              className="mt-4 flex items-center gap-3 rounded-2xl border border-white/8 bg-white/[0.03] px-3 py-3"
            >
              <input
                value={customQuestion}
                onChange={(e) => setCustomQuestion(e.target.value)}
                placeholder="Ask SecureShift AI for guided help"
                className="w-full bg-transparent px-1 text-sm text-on-background outline-none placeholder:text-on-surface-variant"
              />
              <button
                type="submit"
                disabled={isLoading || !customQuestion.trim()}
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-black transition-transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Ask SecureShift AI"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </button>
            </form>
          </GlassFrame>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
