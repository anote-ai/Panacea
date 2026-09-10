import { useState } from 'react';
import OurogenLogo from './OurogenLogo';

interface Step {
  title: string;
  body: string;
  emoji: string;
}

const STEPS: Step[] = [
  {
    emoji: '💬',
    title: 'Chat with your AI assistant',
    body: 'Ask questions, brainstorm, or get help with anything — just type a message below and Ourogen responds in real time.',
  },
  {
    emoji: '📄',
    title: 'Upload documents',
    body: 'Drop in PDFs, DOCX, TXT, or Markdown files. Ourogen reads and indexes them so you can ask questions grounded in your own content.',
  },
  {
    emoji: '🔍',
    title: 'Search your chats',
    body: 'Use the search bar in the sidebar to instantly find past conversations by title or content.',
  },
  {
    emoji: '⚙️',
    title: 'Make it yours',
    body: 'Switch models, toggle dark mode, and manage your account from the menu in the corner. You\'re all set — let\'s get started!',
  },
];

export default function OnboardingTour({ onDone }: { onDone: () => void }) {
  const [step, setStep] = useState(0);
  const isLast = step === STEPS.length - 1;
  const current = STEPS[step];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
      <div className="w-full max-w-md rounded-2xl bg-white dark:bg-[#2F2F2F] shadow-xl p-8">
        <div className="flex flex-col items-center text-center">
          <OurogenLogo className="w-10 h-10 mb-4" />
          <div className="text-4xl mb-4">{current.emoji}</div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {current.title}
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">{current.body}</p>
        </div>

        <div className="flex items-center justify-center gap-2 mb-6">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all ${
                i === step
                  ? 'w-6 bg-gray-900 dark:bg-white'
                  : 'w-1.5 bg-gray-300 dark:bg-gray-600'
              }`}
            />
          ))}
        </div>

        <div className="flex items-center justify-between gap-3">
          <button
            onClick={onDone}
            className="text-sm text-gray-400 dark:text-gray-500 hover:underline"
          >
            Skip
          </button>
          <button
            onClick={() => (isLast ? onDone() : setStep((s) => s + 1))}
            className="px-5 py-2.5 rounded-lg bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
          >
            {isLast ? 'Get started' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
}
