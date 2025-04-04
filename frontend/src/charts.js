// charts.jsx
import React from 'react';
import { Bar, Line, Pie } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export const MistakeChart = ({ data }) => {
  const chartData = {
    labels: ['Blunders', 'Mistakes', 'Inaccuracies'],
    datasets: [{
      label: 'Mistakes by Type',
      data: [data.blunders, data.mistakes, data.inaccuracies],
      backgroundColor: [
        'rgba(239, 68, 68, 0.7)',
        'rgba(249, 115, 22, 0.7)',
        'rgba(234, 179, 8, 0.7)'
      ],
      borderColor: [
        'rgba(239, 68, 68, 1)',
        'rgba(249, 115, 22, 1)',
        'rgba(234, 179, 8, 1)'
      ],
      borderWidth: 1
    }]
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h3 className="font-medium mb-2">Mistake Distribution</h3>
      <Bar 
        data={chartData}
        options={{
          responsive: true,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }}
      />
    </div>
  );
};

export const TimeChart = ({ data }) => {
  const chartData = {
    labels: ['Opening', 'Middlegame', 'Endgame'],
    datasets: [{
      label: 'Mistakes by Game Phase',
      data: [data.opening, data.middlegame, data.endgame],
      backgroundColor: 'rgba(79, 70, 229, 0.7)',
      borderColor: 'rgba(79, 70, 229, 1)',
      borderWidth: 1,
      tension: 0.1
    }]
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h3 className="font-medium mb-2">Mistakes by Game Phase</h3>
      <Line 
        data={chartData}
        options={{
          responsive: true,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }}
      />
    </div>
  );
};

export const OpeningChart = ({ data }) => {
  const topOpenings = data.slice(0, 5);
  const chartData = {
    labels: topOpenings.map(opening => opening.name),
    datasets: [{
      label: 'Mistakes per Opening',
      data: topOpenings.map(opening => opening.mistakes),
      backgroundColor: [
        'rgba(99, 102, 241, 0.7)',
        'rgba(129, 140, 248, 0.7)',
        'rgba(165, 180, 252, 0.7)',
        'rgba(199, 210, 254, 0.7)',
        'rgba(224, 231, 255, 0.7)'
      ],
      borderColor: [
        'rgba(99, 102, 241, 1)',
        'rgba(129, 140, 248, 1)',
        'rgba(165, 180, 252, 1)',
        'rgba(199, 210, 254, 1)',
        'rgba(224, 231, 255, 1)'
      ],
      borderWidth: 1
    }]
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h3 className="font-medium mb-2">Top Openings by Mistakes</h3>
      <Pie 
        data={chartData}
        options={{
          responsive: true,
          plugins: {
            legend: {
              position: 'right'
            }
          }
        }}
      />
    </div>
  );
};