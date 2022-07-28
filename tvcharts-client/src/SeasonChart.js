import React from 'react'
import { useEffect } from 'react'
import { useState } from 'react'
import Chart from 'react-google-charts'

const SeasonChart = ({tconst, type, title, logScale, scaleY, line}) => {

  const [chartData, setChartData] = useState([[1, 1.0, 10]])
  const [maxSeason, setMaxSeason] = useState(10)

  useEffect(() => {
    const url = `http://localhost:5000/season/${tconst}`
    fetch(url).then(
      res => res.json()
    ).then(
      data => {
        setChartData(data)
        const newMaxSeason = data[data.length - 1][0]
        setMaxSeason(newMaxSeason)
      }
    )
  }, [tconst])

  return (
    <Chart
      chartType='ScatterChart'
      data={[["Season Number", 
        (type === "votes") ? {"role": "none"} : "Votes",
        (type === "votes") ? "Votes" : {"role": "none"}], 
        ...chartData]}
      width="100%"
      height="600px"
      loader={"Loading Chart..."}
      options={{
        title: `IMDb ${(type === "votes" ? "Average Votes" : "Rating")} by Season - ${title}`,
        viewWindow: (scaleY) ? {min: 0, max: 10} : {},
        scaleType: (logScale) ? "log" : "linear",
        pointSize: 10,
        lineWidth: (line === true) ? 3 : 0,
        legend: "none",
        hAxis: { 
          title: "Season Number",
          format: 0,
          // viewWindow: {min: 1, maxSe}
          viewWindow: {min: 1, max: maxSeason}},
      }}
    />
  )
}

export default SeasonChart