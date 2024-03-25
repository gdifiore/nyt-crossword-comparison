import chartXkcd from 'chart.xkcd';
import { Bar } from "chart.xkcd-react"

<Bar
config={{
  title: 'github stars VS patron number', // optional
  // xLabel: '', // optional
  // yLabel: '', // optional
  data: {
    labels: ['github stars', 'patrons'],
    datasets: [{
      data: [100, 2],
    }],
  },
  options: { // optional
    yTickCount: 2,
  },
}}
/>