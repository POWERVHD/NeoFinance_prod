/**
 * ChatInterface component - main AI chat interface.
 * Combines all chat components into a complete chat experience.
 */

import React, { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Separator } from '../ui/separator';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { QuickQuestions } from './QuickQuestions';
import { useAIChat } from '../../hooks/useAIChat';
import { Trash2, TrendingUp } from 'lucide-react';

export const ChatInterface = () => {
  const {
    messages,
    isLoading,
    quickQuestions,
    sendMessage,
    analyzeBudget,
    fetchQuickQuestions,
    clearMessages,
  } = useAIChat();

  useEffect(() => {
    fetchQuickQuestions();
  }, [fetchQuickQuestions]);

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>AI Financial Coach</CardTitle>
            <CardDescription>
              Get personalized insights about your spending and budget
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => analyzeBudget(30)}
              disabled={isLoading}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              Analyze Budget
            </Button>
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearMessages}
                disabled={isLoading}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <Separator />

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        <MessageList messages={messages} isLoading={isLoading} />

        <div className="p-4 space-y-3 border-t">
          {messages.length === 0 && (
            <QuickQuestions
              questions={quickQuestions}
              onSelect={sendMessage}
              isLoading={isLoading}
            />
          )}
          <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </div>
      </CardContent>
    </Card>
  );
};
