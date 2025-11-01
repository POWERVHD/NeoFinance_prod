/**
 * MessageList component - scrollable list of chat messages.
 */

import React, { useEffect, useRef } from 'react';
import { ChatBubble } from './ChatBubble';
import { Loader2 } from 'lucide-react';

export const MessageList = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.length === 0 && !isLoading ? (
        <div className="flex items-center justify-center h-full text-center text-muted-foreground">
          <div>
            <p className="text-lg font-medium mb-2">
              Welcome to your AI Financial Coach!
            </p>
            <p className="text-sm">
              Ask me anything about your spending, budgeting, or financial
              health.
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-4 py-2 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-muted-foreground">
                  Thinking...
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
};
