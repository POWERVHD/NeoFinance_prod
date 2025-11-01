/**
 * Home Page Component
 * Main dashboard view showing financial summary
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Dashboard from '../components/Dashboard';
import { dashboardAPI } from '../services/api';
import { Button } from '@/components/ui/button';
import { Loader2, Plus } from 'lucide-react';

function Home() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardSummary();
  }, []);

  const fetchDashboardSummary = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await dashboardAPI.getSummary();
      setSummary(response.data);
    } catch (err) {
      console.error('Failed to fetch dashboard summary:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <div className="rounded-md bg-destructive/15 p-4 text-sm text-destructive border border-destructive/30 max-w-md">
            {error}
          </div>
          <Button onClick={fetchDashboardSummary}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <Link to="/transactions">
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Add Transaction
          </Button>
        </Link>
      </div>

      <Dashboard summary={summary} />
    </div>
  );
}

export default Home;
