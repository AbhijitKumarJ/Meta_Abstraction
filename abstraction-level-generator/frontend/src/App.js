import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [question, setQuestion] = useState('');
  const [abstractions, setAbstractions] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/generate_abstractions/', { raw_question: question });
      setAbstractions(response.data.levels);
    } catch (error) {
      console.error('Error generating abstractions:', error);
    }
    setLoading(false);
  };

  const chartData = {
    labels: abstractions.map(a => `Level ${a.level_number}`),
    datasets: [
      {
        label: 'Abstraction Scores',
        data: abstractions.map(a => a.score),
        fill: false,
        backgroundColor: 'rgb(75, 192, 192)',
        borderColor: 'rgba(75, 192, 192, 0.2)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Abstraction Levels Progression',
      },
    },
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Abstraction Level Generator</h1>
      <form onSubmit={handleSubmit} className="mb-8">
        <textarea
          className="w-full p-2 border rounded"
          rows="4"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your question here..."
        />
        <button
          type="submit"
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Abstractions'}
        </button>
      </form>

      {abstractions.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Abstraction Levels</h2>
          <div className="mb-8">
            <Line data={chartData} options={chartOptions} />
          </div>
          {abstractions.map((abstraction) => (
            <div key={abstraction.level_number} className="mb-4 p-4 border rounded">
              <h3 className="font-bold">Level {abstraction.level_number}</h3>
              <p><strong>Ideal Representation:</strong> {abstraction.ideal_representation}</p>
              <p><strong>Generated Question:</strong> {abstraction.generated_question}</p>
              <p><strong>Score:</strong> {abstraction.score}</p>
              <p><strong>Variables:</strong></p>
              <pre className="bg-gray-100 p-2 rounded">
                {JSON.stringify(abstraction.variables, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
