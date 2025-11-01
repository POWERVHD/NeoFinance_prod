/**
 * TransactionForm Component
 * Form for creating and editing transactions
 */
import { useState, useEffect } from 'react';
import { transactionsAPI } from '../services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';

// Categories constant matching backend
const CATEGORIES = [
  'Food & Dining',
  'Shopping',
  'Transportation',
  'Bills & Utilities',
  'Entertainment',
  'Healthcare',
  'Education',
  'Personal Care',
  'Travel',
  'Income',
  'Other',
];

function TransactionForm({ editingTransaction, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    type: 'expense',
    category: 'Other',
    transaction_date: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Populate form when editing
  useEffect(() => {
    if (editingTransaction) {
      setFormData({
        amount: Math.abs(editingTransaction.amount).toString(),
        description: editingTransaction.description,
        type: editingTransaction.type,
        category: editingTransaction.category,
        transaction_date: editingTransaction.transaction_date,
      });
    }
  }, [editingTransaction]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    // Clear messages when user types
    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleTypeChange = (value) => {
    setFormData({
      ...formData,
      type: value,
    });
    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleCategoryChange = (value) => {
    setFormData({
      ...formData,
      category: value,
    });
    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Please enter a valid amount greater than 0');
      return;
    }

    if (!formData.description.trim()) {
      setError('Please enter a description');
      return;
    }

    setLoading(true);

    try {
      const transactionData = {
        amount: parseFloat(formData.amount),
        description: formData.description,
        type: formData.type,
        category: formData.category,
        transaction_date: formData.transaction_date,
      };

      if (editingTransaction) {
        // Update existing transaction
        await transactionsAPI.update(editingTransaction.id, transactionData);
        setSuccess('Transaction updated successfully!');
      } else {
        // Create new transaction
        await transactionsAPI.create(transactionData);
        setSuccess('Transaction created successfully!');
        // Reset form
        setFormData({
          amount: '',
          description: '',
          type: 'expense',
          category: 'Other',
          transaction_date: new Date().toISOString().split('T')[0],
        });
      }

      // Notify parent component
      if (onSuccess) {
        setTimeout(() => {
          onSuccess();
        }, 1000);
      }
    } catch (err) {
      console.error('Transaction error:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to save transaction. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      amount: '',
      description: '',
      type: 'expense',
      category: 'Other',
      transaction_date: new Date().toISOString().split('T')[0],
    });
    setError('');
    setSuccess('');
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{editingTransaction ? 'Edit Transaction' : 'Add New Transaction'}</CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 rounded-md bg-destructive/15 p-3 text-sm text-destructive border border-destructive/30">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 rounded-md bg-green-500/15 p-3 text-sm text-green-700 dark:text-green-400 border border-green-500/30">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="amount">Amount ($)</Label>
              <Input
                type="number"
                id="amount"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                placeholder="0.00"
                step="0.01"
                min="0.01"
                disabled={loading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="transaction_date">Date</Label>
              <Input
                type="date"
                id="transaction_date"
                name="transaction_date"
                value={formData.transaction_date}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              type="text"
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Enter transaction description"
              disabled={loading}
              required
            />
          </div>

          <div className="space-y-2">
            <Label>Type</Label>
            <RadioGroup
              value={formData.type}
              onValueChange={handleTypeChange}
              disabled={loading}
              className="flex gap-4"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="expense" id="expense" />
                <Label htmlFor="expense" className="font-normal cursor-pointer">
                  Expense
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="income" id="income" />
                <Label htmlFor="income" className="font-normal cursor-pointer">
                  Income
                </Label>
              </div>
            </RadioGroup>
          </div>

          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select
              value={formData.category}
              onValueChange={handleCategoryChange}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Saving...' : editingTransaction ? 'Update Transaction' : 'Add Transaction'}
            </Button>
            {editingTransaction && (
              <Button
                type="button"
                variant="outline"
                onClick={handleCancel}
                disabled={loading}
              >
                Cancel
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

export default TransactionForm;
