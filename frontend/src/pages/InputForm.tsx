import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface FormData {
  ticker: string;
  showReasoning: boolean;
  initialCapital: number;
  numOfNews: number;
  startDate: string;
  endDate: string;
  initialPosition: number;
}

const InputForm: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    ticker: '',
    showReasoning: true,
    initialCapital: 100000,
    numOfNews: 5,
    startDate: '',
    endDate: '',
    initialPosition: 0,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Build request payload
      const payload = {
        ticker: formData.ticker,
        show_reasoning: formData.showReasoning,
        initial_capital: formData.initialCapital,
        num_of_news: formData.numOfNews,
        initial_position: formData.initialPosition,
        start_date: formData.startDate || undefined,
        end_date: formData.endDate || undefined,
      };

      // Submit analysis request
      const response = await axios.post('http://localhost:8000/api/analysis/start', payload);

      if (response.data.success) {
        const runId = response.data.data?.run_id;
        if (runId) {
          // Poll analysis status
          const pollStatus = async () => {
            try {
              const statusResp = await axios.get(`http://localhost:8000/api/analysis/${runId}/status`);
              const status = statusResp.data.data?.status;
              if (status === 'completed') {
                // Analysis complete, navigate to results page
                navigate(`/result?run_id=${runId}`);
              } else if (status === 'error') {
                alert('Analysis failed');
                setIsLoading(false);
              } else {
                setTimeout(pollStatus, 2000); // Poll again after 2 seconds
              }
            } catch (err) {
              alert('Failed to get analysis status');
              setIsLoading(false);
            }
          };
          pollStatus();
        } else {
          alert('Analysis task submitted, but no run ID received');
          setIsLoading(false);
        }
      } else {
        alert(response.data.message || 'Failed to submit analysis task');
        setIsLoading(false);
      }
    } catch (error) {
      alert('An error occurred during analysis, please try again');
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
      <h1 className="text-2xl font-bold mb-6 text-center">Stock Analysis System</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Stock Code *</label>
          <input
            type="text"
            required
            value={formData.ticker}
            onChange={(e) => setFormData({ ...formData, ticker: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="e.g., 002848"
          />
          <p className="mt-1 text-sm text-gray-500">Please enter the stock code, e.g., "002848"</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Initial Capital</label>
          <input
            type="number"
            min="0"
            step="1000"
            value={formData.initialCapital}
            onChange={(e) => setFormData({ ...formData, initialCapital: Number(e.target.value) })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">Default: 100,000</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Number of News</label>
          <input
            type="number"
            min="1"
            max="100"
            value={formData.numOfNews}
            onChange={(e) => setFormData({ ...formData, numOfNews: Number(e.target.value) })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Start Date</label>
          <input
            type="date"
            value={formData.startDate}
            onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">End Date</label>
          <input
            type="date"
            value={formData.endDate}
            onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Initial Position</label>
          <input
            type="number"
            min="0"
            value={formData.initialPosition}
            onChange={(e) => setFormData({ ...formData, initialPosition: Number(e.target.value) })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">Default: 0</p>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            checked={formData.showReasoning}
            onChange={(e) => setFormData({ ...formData, showReasoning: e.target.checked })}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label className="ml-2 block text-sm text-gray-900">Show Analysis Reasoning</label>
          <p className="ml-2 text-sm text-gray-500">Default: Enabled</p>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {isLoading ? 'Analyzing...' : 'Start Analysis'}
        </button>
      </form>
    </div>
  );
};

export default InputForm; 