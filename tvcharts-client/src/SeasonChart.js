import React from 'react'
import { useEffect } from 'react'
import { useState } from 'react'
import Chart from 'react-google-charts'

const SeasonChart = ({tconst, type, title, logScale, scaleY, line, curved}) => {

  const [chartData, setChartData] = useState([[1, 1.0, 10]])
  const [maxSeason, setMaxSeason] = useState(10)

  useEffect(() => {
    const url = `http://localhost:5000/season/${tconst}`
    fetch(url).then(
      res => res.json()
    ).then(
      data => {
        for (let i = 0; i < data.length; i++) {
          const annotation = `<b>Season ${data[i][0]}</b><br/>${data[i][2].toLocaleString("en-us")} Votes<br/>${data[i][1].toLocaleString("en-us")} Average Rating<br/>`
          data[i].push(annotation)
        }
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
        (type === "votes") ? "Votes" : {"role": "none"}, 
        { role: "tooltip", type: "string", p: { html: true }}],
        ...chartData]}
      width="100%"
      height="600px"
      loader={"Loading Chart..."}
      options={{
        title: `Average IMDb ${(type === "votes" ? "Votes" : "Rating")} by Season - ${title}`,
        viewWindow: (scaleY) ? {min: 0, max: 10} : {},
        scaleType: (logScale) ? "log" : "linear",
        pointSize: 10,
        lineWidth: (line === true) ? 3 : 0,
        legend: "none",
        tooltip: { isHtml: true, trigger: 'both' },
        hAxis: { 
          title: "Season Number",
          format: 0,
          viewWindow: {min: 1, max: maxSeason}},
        vAxis: {
          title: (type === "rating" ? "Average Rating" : "Number of Votes")
        },
        curveType: (curved === true) ? 'function' : 'none'
      }}
    />
  )
}

export default SeasonChart