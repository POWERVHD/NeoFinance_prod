/**
 * ChatInput component - input field for sending chat messages.
 */

import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Send } from 'lucide-react';

export const ChatInput = ({ onSend, isLoading, disabled }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading && !disabled) {
      onSend(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="text"
        placeholder="Ask me about your finances..."
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        disabled={isLoading || disabled}
        maxLength={500}
        className="flex-1"
      />
      <Button
        type="submit"
        disabled={!inputValue.trim() || isLoading || disabled}
        size="icon"
      >
        <Send className="h-4 w-4" />
      </Button>
    </form>
  );
};
