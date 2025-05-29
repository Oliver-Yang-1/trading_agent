import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';

const AnalysisResult: React.FC = () => {
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const runId = query.get('run_id');

  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) {
      setError('未指定分析任务');
      setLoading(false);
      return;
    }
    const fetchReport = async () => {
      try {
        const resp = await axios.get(`http://localhost:8000/api/analysis/${runId}/structured_log`);
        if (resp.data.success && resp.data.data && resp.data.data.content) {
          setReport(resp.data.data.content);
        } else {
          setError('分析报告格式错误');
        }
      } catch (err) {
        console.error('获取分析报告失败:', err);
        setError('获取分析报告失败');
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [runId]);

  const handleSave = () => {
    const blob = new Blob([report], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis_report_${runId || 'unknown'}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-gray-50 min-h-screen">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-2xl font-bold mb-6 text-center">Latest Analysis Results</h1>
        <div className="flex justify-end mb-4">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
            onClick={handleSave}
            disabled={!report}
          >
            SAVE
          </button>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg overflow-x-auto border">
          {loading && <div>Loading...</div>}
          {error && <div className="text-red-500">{error}</div>}
          {!loading && !error && (
            <pre className="whitespace-pre-wrap font-mono text-base">{report}</pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalysisResult; 