/**
 * Custom hook for AI Chat functionality.
 * Handles chat messages, quick questions, and budget analysis.
 */

import { useState, useCallback } from 'react';
import api from '../services/api';

export const useAIChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [quickQuestions, setQuickQuestions] = useState([]);

  // Fetch quick questions
  const fetchQuickQuestions = useCallback(async () => {
    try {
      const response = await api.get('/ai-chat/quick-questions');
      setQuickQuestions(response.data.questions);
    } catch (error) {
      console.error('Failed to fetch quick questions:', error);
    }
  }, []);

  // Send a chat message
  const sendMessage = useCallback(async (question, includeContext = true) => {
    if (!question.trim()) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now().toString(),
      text: question,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    setIsLoading(true);
    try {
      const response = await api.post('/ai-chat/message', {
        question,
        include_context: includeContext,
      });

      // Add AI response to chat
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        isUser: false,
        timestamp: new Date(response.data.timestamp),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);

      // Add error message
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Request budget analysis
  const analyzeBudget = useCallback(async (periodDays = 30) => {
    const analysisMessage = {
      id: Date.now().toString(),
      text: `Analyze my budget for the last ${periodDays} days`,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, analysisMessage]);

    setIsLoading(true);
    try {
      const response = await api.post('/ai-chat/analyze-budget', {
        period_days: periodDays,
      });

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        isUser: false,
        timestamp: new Date(response.data.timestamp),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Failed to analyze budget:', error);

      const errorMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I could not analyze your budget. Please try again.',
        isUser: false,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Clear chat history
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    quickQuestions,
    sendMessage,
    analyzeBudget,
    fetchQuickQuestions,
    clearMessages,
  };
};
