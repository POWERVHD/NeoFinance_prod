/**
 * Transactions Page Component
 * Manages all transactions with create, edit, and delete functionality
 */
import { useState, useEffect } from 'react';
import TransactionForm from '../components/TransactionForm';
import TransactionList from '../components/TransactionList';
import { transactionsAPI } from '../services/api';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingTransaction, setEditingTransaction] = useState(null);

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await transactionsAPI.getAll();
      setTransactions(response.data);
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
      setError('Failed to load transactions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFormSuccess = () => {
    // Refresh transactions list after create/update
    fetchTransactions();
    // Clear editing mode
    setEditingTransaction(null);
  };

  const handleEdit = (transaction) => {
    // Scroll to top to show form
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setEditingTransaction(transaction);
  };

  const handleCancelEdit = () => {
    setEditingTransaction(null);
  };

  const handleDelete = () => {
    // Refresh transactions list after delete
    fetchTransactions();
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Transactions</h1>
      </div>

      {/* Transaction Form */}
      <div className="mb-6">
        <TransactionForm
          editingTransaction={editingTransaction}
          onSuccess={handleFormSuccess}
          onCancel={handleCancelEdit}
        />
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-12 gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading transactions...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="flex flex-col items-center justify-center py-12 gap-4">
          <div className="rounded-md bg-destructive/15 p-4 text-sm text-destructive border border-destructive/30 max-w-md">
            {error}
          </div>
          <Button onClick={fetchTransactions}>
            Try Again
          </Button>
        </div>
      )}

      {/* Transaction List */}
      {!loading && !error && (
        <TransactionList
          transactions={transactions}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}

export default Transactions;
