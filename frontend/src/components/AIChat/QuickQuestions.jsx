/**
 * QuickQuestions component - displays suggested questions as chips.
 */

import React from 'react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';

export const QuickQuestions = ({ questions, onSelect, isLoading }) => {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="space-y-2">
      <p className="text-sm text-muted-foreground font-medium">
        Quick Questions:
      </p>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <Badge
            key={index}
            variant="outline"
            className="cursor-pointer hover:bg-accent transition-colors px-3 py-1"
            onClick={() => !isLoading && onSelect(question)}
          >
            {question}
          </Badge>
        ))}
      </div>
    </div>
  );
};
