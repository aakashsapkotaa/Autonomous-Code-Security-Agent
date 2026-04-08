'use client';

import { FormEvent, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Bot, MessageSquare, Send, X } from 'lucide-react';
import GlassFrame from './GlassFrame';

const quickPrompts = [
  'How do I sign in?',
  'What does SecureShift monitor?',
  'How do I recover access?',
];

const answers: Record<string, string> = {
  'How do I sign in?':
    'Use your operator email and security token in the Access Console, then select Establish Connection.',
  'What does SecureShift monitor?':
    'SecureShift monitors security activity, threat signals, and infrastructure status from one dashboard.',
  'How do I recover access?':
    'Use the Recovery required link in the console and follow the guided recovery flow for your operator account.',
};

const fallbackResponse =
  'SecureShift AI can help with sign-in, monitoring coverage, console recovery, and navigation across the dashboard.';

interface HelpBotProps {
  open: boolean;
  onClose: () => void;
}

export default function HelpBot({ open, onClose }: HelpBotProps) {
  const [selectedPrompt, setSelectedPrompt] = useState(quickPrompts[0]);
  const [customQuestion, setCustomQuestion] = useState('');
  const response = useMemo(() => answers[selectedPrompt] ?? fallbackResponse, [selectedPrompt]);

  const handlePromptSelect = (prompt: string) => {
    setSelectedPrompt(prompt);
    setCustomQuestion('');
  };

  const handleAsk = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const normalized = customQuestion.trim().toLowerCase();
    if (!normalized) {
      return;
    }

    if (normalized.includes('sign') || normalized.includes('login') || normalized.includes('log in')) {
      setSelectedPrompt('How do I sign in?');
      return;
    }

    if (
      normalized.includes('monitor') ||
      normalized.includes('track') ||
      normalized.includes('dashboard') ||
      normalized.includes('secure')
    ) {
      setSelectedPrompt('What does SecureShift monitor?');
      return;
    }

    if (
      normalized.includes('recover') ||
      normalized.includes('access') ||
      normalized.includes('password') ||
      normalized.includes('token')
    ) {
      setSelectedPrompt('How do I recover access?');
      return;
    }

    setSelectedPrompt(customQuestion.trim());
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
                  <MessageSquare className="h-4 w-4" />
                </span>
                <div>
                  <p className="text-sm font-medium text-on-background">{selectedPrompt}</p>
                  <p className="mt-2 text-sm leading-6 text-on-surface-variant">{response}</p>
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
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white text-black transition-transform hover:scale-105"
                aria-label="Ask SecureShift AI"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </GlassFrame>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
